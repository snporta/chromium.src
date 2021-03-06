// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/extensions/api/bluetooth_low_energy/bluetooth_low_energy_connection.h"

namespace extensions {

static base::LazyInstance<BrowserContextKeyedAPIFactory<
    ApiResourceManager<BluetoothLowEnergyConnection> > > g_factory =
    LAZY_INSTANCE_INITIALIZER;

template <>
BrowserContextKeyedAPIFactory<
    ApiResourceManager<BluetoothLowEnergyConnection> >*
ApiResourceManager<BluetoothLowEnergyConnection>::GetFactoryInstance() {
  return g_factory.Pointer();
}

BluetoothLowEnergyConnection::BluetoothLowEnergyConnection(
    bool persistent,
    const std::string& owner_extension_id,
    scoped_ptr<device::BluetoothGattConnection> connection)
    : ApiResource(owner_extension_id),
      persistent_(persistent),
      connection_(connection.release()) {
}

BluetoothLowEnergyConnection::~BluetoothLowEnergyConnection() {
}

device::BluetoothGattConnection*
BluetoothLowEnergyConnection::GetConnection() const {
  return connection_.get();
}

bool BluetoothLowEnergyConnection::IsPersistent() const {
  return persistent_;
}

}  // namespace extensions
