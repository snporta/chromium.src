// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "net/base/network_change_notifier.h"
#include "net/base/network_change_notifier_factory.h"
#include "base/metrics/histogram.h"
#include "build/build_config.h"
#include "googleurl/src/gurl.h"
#include "net/base/net_util.h"
#if defined(OS_WIN)
#include "net/base/network_change_notifier_win.h"
#elif defined(OS_LINUX) && !defined(OS_CHROMEOS)
#include "net/base/network_change_notifier_linux.h"
#elif defined(OS_MACOSX)
#include "net/base/network_change_notifier_mac.h"
#endif

namespace net {

namespace {

// The actual singleton notifier.  The class contract forbids usage of the API
// in ways that would require us to place locks around access to this object.
// (The prohibition on global non-POD objects makes it tricky to do such a thing
// anyway.)
NetworkChangeNotifier* g_network_change_notifier = NULL;

// Class factory singleton.
NetworkChangeNotifierFactory* g_network_change_notifier_factory = NULL;

class MockNetworkChangeNotifier : public NetworkChangeNotifier {
 public:
  virtual ConnectionType GetCurrentConnectionType() const OVERRIDE {
    return CONNECTION_UNKNOWN;
  }
};

}  // namespace

// The main observer class that records UMAs for network events.
class HistogramWatcher
    : public NetworkChangeNotifier::ConnectionTypeObserver,
      public NetworkChangeNotifier::IPAddressObserver,
      public NetworkChangeNotifier::DNSObserver {
 public:
  HistogramWatcher()
      : last_ip_address_change_(base::TimeTicks::Now()),
        last_connection_change_(base::TimeTicks::Now()),
        last_dns_change_(base::TimeTicks::Now()),
        last_connection_type_(NetworkChangeNotifier::CONNECTION_UNKNOWN),
        offline_packets_received_(0) {}

  // Registers our three Observer implementations.  This is called from the
  // network thread so that our Observer implementations are also called
  // from the network thread.  This avoids multi-threaded race conditions
  // because the only other interface, |NotifyDataReceived| is also
  // only called from the network thread.
  void InitHistogramWatcher() {
    NetworkChangeNotifier::AddConnectionTypeObserver(this);
    NetworkChangeNotifier::AddIPAddressObserver(this);
    NetworkChangeNotifier::AddDNSObserver(this);
  }

  virtual ~HistogramWatcher() {}

  // NetworkChangeNotifier::IPAddressObserver implementation.
  virtual void OnIPAddressChanged() OVERRIDE {
    UMA_HISTOGRAM_MEDIUM_TIMES("NCN.IPAddressChange",
                               SinceLast(&last_ip_address_change_));
  }

  // NetworkChangeNotifier::ConnectionTypeObserver implementation.
  virtual void OnConnectionTypeChanged(
      NetworkChangeNotifier::ConnectionType type) OVERRIDE {
    if (type != NetworkChangeNotifier::CONNECTION_NONE) {
      UMA_HISTOGRAM_MEDIUM_TIMES("NCN.OnlineChange",
                                 SinceLast(&last_connection_change_));

      if (offline_packets_received_) {
        if ((last_connection_change_ - last_offline_packet_received_) <
            base::TimeDelta::FromSeconds(5)) {
          // We can compare this sum with the sum of NCN.OfflineDataRecv.
          UMA_HISTOGRAM_COUNTS_10000(
              "NCN.OfflineDataRecvAny5sBeforeOnline",
              offline_packets_received_);
        }

        UMA_HISTOGRAM_MEDIUM_TIMES("NCN.OfflineDataRecvUntilOnline",
                                   last_connection_change_ -
                                       last_offline_packet_received_);
      }
    } else {
      UMA_HISTOGRAM_MEDIUM_TIMES("NCN.OfflineChange",
                                 SinceLast(&last_connection_change_));
    }

    offline_packets_received_ = 0;
    last_connection_type_ = type;
  }

  // NetworkChangeNotifier::DNSObserver implementation.
  virtual void OnDNSChanged(unsigned detail) OVERRIDE {
    if (detail == NetworkChangeNotifier::CHANGE_DNS_SETTINGS) {
      UMA_HISTOGRAM_MEDIUM_TIMES("NCN.DNSConfigChange",
                                 SinceLast(&last_dns_change_));
    }
  }

  // Record histogram data whenever we receive a packet but think we're
  // offline.  Should only be called from the network thread.
  void NotifyDataReceived(const GURL& source) {
    if (last_connection_type_ != NetworkChangeNotifier::CONNECTION_NONE ||
        IsLocalhost(source.host()) ||
        !(source.SchemeIs("http") || source.SchemeIs("https"))) {
      return;
    }

    base::TimeTicks current_time = base::TimeTicks::Now();
    UMA_HISTOGRAM_MEDIUM_TIMES("NCN.OfflineDataRecv",
                               current_time - last_connection_change_);
    offline_packets_received_++;
    last_offline_packet_received_ = current_time;
  }

 private:
  static base::TimeDelta SinceLast(base::TimeTicks *last_time) {
    base::TimeTicks current_time = base::TimeTicks::Now();
    base::TimeDelta delta = current_time - *last_time;
    *last_time = current_time;
    return delta;
  }

  base::TimeTicks last_ip_address_change_;
  base::TimeTicks last_connection_change_;
  base::TimeTicks last_dns_change_;
  base::TimeTicks last_offline_packet_received_;
  NetworkChangeNotifier::ConnectionType last_connection_type_;
  int32 offline_packets_received_;

  DISALLOW_COPY_AND_ASSIGN(HistogramWatcher);
};

NetworkChangeNotifier::~NetworkChangeNotifier() {
  DCHECK_EQ(this, g_network_change_notifier);
  g_network_change_notifier = NULL;
}

// static
void NetworkChangeNotifier::SetFactory(
    NetworkChangeNotifierFactory* factory) {
  CHECK(!g_network_change_notifier_factory);
  g_network_change_notifier_factory = factory;
}

// static
NetworkChangeNotifier* NetworkChangeNotifier::Create() {
  if (g_network_change_notifier_factory)
    return g_network_change_notifier_factory->CreateInstance();

#if defined(OS_WIN)
  NetworkChangeNotifierWin* network_change_notifier =
      new NetworkChangeNotifierWin();
  network_change_notifier->WatchForAddressChange();
  return network_change_notifier;
#elif defined(OS_CHROMEOS) || defined(OS_ANDROID)
  // ChromeOS and Android builds MUST use their own class factory.
#if !defined(OS_CHROMEOS)
  // TODO(oshima): ash_shell do not have access to chromeos'es
  // notifier yet. Re-enable this when chromeos'es notifier moved to
  // chromeos root directory. crbug.com/119298.
  CHECK(false);
#endif
  return NULL;
#elif defined(OS_LINUX)
  return NetworkChangeNotifierLinux::Create();
#elif defined(OS_MACOSX)
  return new NetworkChangeNotifierMac();
#else
  NOTIMPLEMENTED();
  return NULL;
#endif
}

// static
NetworkChangeNotifier::ConnectionType
NetworkChangeNotifier::GetConnectionType() {
  return g_network_change_notifier ?
      g_network_change_notifier->GetCurrentConnectionType() :
      CONNECTION_UNKNOWN;
}

// static
void NetworkChangeNotifier::NotifyDataReceived(const GURL& source) {
  if (!g_network_change_notifier)
    return;
  g_network_change_notifier->histogram_watcher_->NotifyDataReceived(source);
}

// static
void NetworkChangeNotifier::InitHistogramWatcher() {
  if (!g_network_change_notifier)
    return;
  g_network_change_notifier->histogram_watcher_->InitHistogramWatcher();
}

#if defined(OS_LINUX)
// static
const internal::AddressTrackerLinux*
NetworkChangeNotifier::GetAddressTracker() {
  return g_network_change_notifier ?
        g_network_change_notifier->GetAddressTrackerInternal() : NULL;
}
#endif

// static
bool NetworkChangeNotifier::IsWatchingDNS() {
  if (!g_network_change_notifier)
    return false;
  base::AutoLock lock(g_network_change_notifier->watching_dns_lock_);
  return g_network_change_notifier->watching_dns_;
}

// static
NetworkChangeNotifier* NetworkChangeNotifier::CreateMock() {
  return new MockNetworkChangeNotifier();
}

void NetworkChangeNotifier::AddIPAddressObserver(IPAddressObserver* observer) {
  if (g_network_change_notifier)
    g_network_change_notifier->ip_address_observer_list_->AddObserver(observer);
}

void NetworkChangeNotifier::AddConnectionTypeObserver(
    ConnectionTypeObserver* observer) {
  if (g_network_change_notifier) {
    g_network_change_notifier->connection_type_observer_list_->AddObserver(
        observer);
  }
}

void NetworkChangeNotifier::AddDNSObserver(DNSObserver* observer) {
  if (g_network_change_notifier) {
    g_network_change_notifier->resolver_state_observer_list_->AddObserver(
        observer);
  }
}

void NetworkChangeNotifier::RemoveIPAddressObserver(
    IPAddressObserver* observer) {
  if (g_network_change_notifier) {
    g_network_change_notifier->ip_address_observer_list_->RemoveObserver(
        observer);
  }
}

void NetworkChangeNotifier::RemoveConnectionTypeObserver(
    ConnectionTypeObserver* observer) {
  if (g_network_change_notifier) {
    g_network_change_notifier->connection_type_observer_list_->RemoveObserver(
        observer);
  }
}

void NetworkChangeNotifier::RemoveDNSObserver(DNSObserver* observer) {
  if (g_network_change_notifier) {
    g_network_change_notifier->resolver_state_observer_list_->RemoveObserver(
        observer);
  }
}

NetworkChangeNotifier::NetworkChangeNotifier()
    : ip_address_observer_list_(
        new ObserverListThreadSafe<IPAddressObserver>(
            ObserverListBase<IPAddressObserver>::NOTIFY_EXISTING_ONLY)),
      connection_type_observer_list_(
        new ObserverListThreadSafe<ConnectionTypeObserver>(
            ObserverListBase<ConnectionTypeObserver>::NOTIFY_EXISTING_ONLY)),
      resolver_state_observer_list_(
        new ObserverListThreadSafe<DNSObserver>(
            ObserverListBase<DNSObserver>::NOTIFY_EXISTING_ONLY)),
      watching_dns_(false) {
  DCHECK(!g_network_change_notifier);
  g_network_change_notifier = this;
  histogram_watcher_.reset(new HistogramWatcher());
}

#if defined(OS_LINUX)
const internal::AddressTrackerLinux*
NetworkChangeNotifier::GetAddressTrackerInternal() const {
  return NULL;
}
#endif

// static
void NetworkChangeNotifier::NotifyObserversOfIPAddressChange() {
  if (g_network_change_notifier) {
    g_network_change_notifier->ip_address_observer_list_->Notify(
        &IPAddressObserver::OnIPAddressChanged);
  }
}

// static
void NetworkChangeNotifier::NotifyObserversOfDNSChange(unsigned detail) {
  if (g_network_change_notifier) {
    {
      base::AutoLock lock(g_network_change_notifier->watching_dns_lock_);
      if (detail & NetworkChangeNotifier::CHANGE_DNS_WATCH_STARTED) {
        g_network_change_notifier->watching_dns_ = true;
      } else if (detail & NetworkChangeNotifier::CHANGE_DNS_WATCH_FAILED) {
        g_network_change_notifier->watching_dns_ = false;
      }
      // Include detail that watch is off to spare the call to IsWatchingDNS.
      if (!g_network_change_notifier->watching_dns_)
        detail |= NetworkChangeNotifier::CHANGE_DNS_WATCH_FAILED;
    }
    DCHECK(!(detail & NetworkChangeNotifier::CHANGE_DNS_WATCH_FAILED) ||
           !(detail & NetworkChangeNotifier::CHANGE_DNS_WATCH_STARTED));
    g_network_change_notifier->resolver_state_observer_list_->Notify(
        &DNSObserver::OnDNSChanged, detail);
  }
}

void NetworkChangeNotifier::NotifyObserversOfConnectionTypeChange() {
  if (g_network_change_notifier) {
    g_network_change_notifier->connection_type_observer_list_->Notify(
        &ConnectionTypeObserver::OnConnectionTypeChanged,
        GetConnectionType());
  }
}

NetworkChangeNotifier::DisableForTest::DisableForTest()
    : network_change_notifier_(g_network_change_notifier) {
  DCHECK(g_network_change_notifier);
  g_network_change_notifier = NULL;
}

NetworkChangeNotifier::DisableForTest::~DisableForTest() {
  DCHECK(!g_network_change_notifier);
  g_network_change_notifier = network_change_notifier_;
}

}  // namespace net
