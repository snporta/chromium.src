// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/**
 * @fileoverview
 * Module to support logging debug messages.
 */

'use strict';

/** @suppress {duplicate} */
var remoting = remoting || {};

/**
 * @constructor
 * @param {Element} logElement The HTML div to which to add log messages.
 * @param {Element} statsElement The HTML div to which to update stats.
 */
remoting.DebugLog = function(logElement, statsElement) {
  this.logElement = logElement;
  this.statsElement = statsElement;
  this.clientJid = '';
  this.hostJid = '';
};

/**
 * Maximum number of lines to record in the debug log. Only the most
 * recent <n> lines are displayed.
 */
remoting.DebugLog.prototype.MAX_DEBUG_LOG_SIZE = 1000;

/**
 * Add the given message to the debug log.
 *
 * @param {number} indentLevel The indention level for this message.
 * @param {string} message The debug info to add to the log.
 */
remoting.DebugLog.prototype.logIndent = function(indentLevel, message) {
  // Remove lines from top if we've hit our max log size.
  if (this.logElement.childNodes.length == this.MAX_DEBUG_LOG_SIZE) {
    this.logElement.removeChild(this.logElement.firstChild);
  }

  // Add the new <p> to the end of the debug log.
  var p = document.createElement('p');
  if (indentLevel == 1) {
    p.className = 'indent';
  } else if (indentLevel > 1) {
    p.className = 'indent2';
  }
  p.appendChild(document.createTextNode(message));
  this.logElement.appendChild(p);

  // Scroll to bottom of div
  this.logElement.scrollTop = this.logElement.scrollHeight;
};

/**
 * Add the given message to the debug log.
 *
 * @param {string} message The debug info to add to the log.
 */
remoting.DebugLog.prototype.log = function(message) {
  this.logIndent(0, message);
}

/**
 * Show or hide the debug log.
 */
remoting.DebugLog.prototype.toggle = function() {
  var debugLog = /** @type {Element} */ this.logElement.parentNode;
  if (debugLog.hidden) {
    debugLog.hidden = false;
  } else {
    debugLog.hidden = true;
  }
};

/**
 * Update the statistics panel.
 * @param {Object.<string, number>} stats The connection statistics.
 */
remoting.DebugLog.prototype.updateStatistics = function(stats) {
  var units = '';
  var videoBandwidth = stats['video_bandwidth'];
  if (videoBandwidth < 1024) {
    units = 'Bps';
  } else if (videoBandwidth < 1048576) {
    units = 'KiBps';
    videoBandwidth = videoBandwidth / 1024;
  } else if (videoBandwidth < 1073741824) {
    units = 'MiBps';
    videoBandwidth = videoBandwidth / 1048576;
  } else {
    units = 'GiBps';
    videoBandwidth = videoBandwidth / 1073741824;
  }

  var statistics = document.getElementById('statistics');
  this.statsElement.innerText =
      'Bandwidth: ' + videoBandwidth.toFixed(2) + units +
      ', Frame Rate: ' +
          (stats['video_frame_rate'] ?
           stats['video_frame_rate'].toFixed(2) + ' fps' : 'n/a') +
      ', Capture: ' + stats['capture_latency'].toFixed(2) + 'ms' +
      ', Encode: ' + stats['encode_latency'].toFixed(2) + 'ms' +
      ', Decode: ' + stats['decode_latency'].toFixed(2) + 'ms' +
      ', Render: ' + stats['render_latency'].toFixed(2) + 'ms' +
      ', Latency: ' + stats['roundtrip_latency'].toFixed(2) + 'ms';
};

/**
 * Check for the debug toggle hot-key.
 *
 * @param {Event} event The keyboard event.
 * @return {void} Nothing.
 */
remoting.DebugLog.onKeydown = function(event) {
  if (String.fromCharCode(event.which) == 'D') {
    remoting.debug.toggle();
  }
};

/**
 * Record the client and host JIDs so that we can check them against the
 * params in the IQ packets.
 *
 * @param {string} clientJid The client JID string.
 * @param {string} hostJid The host JID string.
 */
remoting.DebugLog.prototype.setJids = function(clientJid, hostJid) {
  this.clientJid = clientJid;
  this.hostJid = hostJid;
}

/**
 * Calculate the 'pretty' version of data from the |server| node and return
 * it as a string.
 *
 * @param {Node} server Xml node with server info.
 *
 * @return {string} Prettified-version of |server| node.
 */
remoting.DebugLog.prototype.calcServerString = function(server) {
  var host = server.getAttribute('host');
  var udp = server.getAttribute('udp');
  var tcp = server.getAttribute('tcp');
  var tcpssl = server.getAttribute('tcpssl');

  var str = "'" + host + "'";
  if (udp)
    str = str + ' udp:' + udp;
  if (tcp)
    str = str + ' tcp:' + tcp;
  if (tcpssl)
    str = str + ' tcpssl:' + tcpssl;

  str = str + '; ';
  return str;
};

/**
 * Calc the 'pretty' version of channel data and return it as a string.
 *
 * @param {Node} channel Xml node with channel info.
 *
 * @return {string} Prettified-version of |channel| node.
 */
remoting.DebugLog.prototype.calcChannelString = function(channel) {
  var name = channel.nodeName;
  var transport = channel.getAttribute('transport');
  var version = channel.getAttribute('version');
  var desc = name + ' ' + transport + ' v' + version;
  if (name == 'video') {
    desc = desc + ' codec=' + channel.getAttribute('codec');
  }
  return desc + '; ';
}

/**
 * Pretty print the jingleinfo from the given Xml node.
 *
 * @param {Node} query Xml query node with jingleinfo in the child nodes.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettyJingleinfo = function(query) {
  var nodes = query.childNodes;
  var stun_servers = '';
  for (var i = 0; i < nodes.length; i++) {
    /** @type {Node} */
    var node = nodes[i];
    var name = node.nodeName;
    if (name == 'stun') {
      var sserver = '';
      var stun_nodes = node.childNodes;
      for(var s = 0; s < stun_nodes.length; s++) {
        /** @type {Node} */
        var stun_node = stun_nodes[s];
        var sname = stun_node.nodeName;
        if (sname == 'server') {
          sserver = sserver + this.calcServerString(stun_node);
        }
      }
      this.logIndent(1, 'stun ' + sserver);
    } else if (name == 'relay') {
      var token = 'token: ';
      var rserver = '';
      var relay_nodes = node.childNodes;
      for(var r = 0; r < relay_nodes.length; r++) {
        /** @type {Node} */
        var relay_node = relay_nodes[r];
        var rname = relay_node.nodeName;
        if (rname == 'token') {
          token = token + relay_node.textContent;
        }
        if (rname == 'server') {
          rserver = rserver + this.calcServerString(relay_node);
        }
      }
      this.logIndent(1, 'relay ' + rserver + token);
    } else {
      return false;
    }
  }

  return true;
};

/**
 * Pretty print the session-initiate or session-accept info from the given
 * Xml node.
 *
 * @param {Node} jingle Xml node with jingle session-initiate or session-accept
 *                      info contained in child nodes.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettySessionInitiateAccept = function(jingle) {
  if (jingle.childNodes.length != 1) {
    return false;
  }
  var content = jingle.firstChild;
  if (content.nodeName != 'content') {
    return false;
  }
  var content_children = content.childNodes;
  for (var c = 0; c < content_children.length; c++) {
    /** @type {Node} */
    var content_child = content_children[c];
    var cname = content_child.nodeName;
    if (cname == 'description') {
      var channels = '';
      var resolution = '';
      var auth = '';
      var desc_children = content_child.childNodes;
      for (var d = 0; d < desc_children.length; d++) {
        /** @type {Node} */
        var desc = desc_children[d];
        var dname = desc.nodeName;
        if (dname == 'control' || dname == 'event' || dname == 'video') {
          channels = channels + this.calcChannelString(desc);
        } else if (dname == 'initial-resolution') {
          resolution = desc.getAttribute('width') + 'x' +
              desc.getAttribute('height');
        } else if (dname == 'authentication') {
          var auth_children = desc.childNodes;
          for (var a = 0; a < auth_children.length; a++) {
            /** @type {Node} */
            var auth_info = auth_children[a];
            if (auth_info.nodeName == 'auth-token') {
              auth = auth + ' (auth-token) ' + auth_info.textContent;
            } else if (auth_info.nodeName == 'certificate') {
              auth = auth + ' (certificate) ' + auth_info.textContent;
            } else if (auth_info.nodeName == 'master-key') {
              auth = auth + ' (master-key) ' + auth_info.textContent;
            } else {
              return false;
            }
          }
        } else {
          return false;
        }
      }
      this.logIndent(1, 'channels: ' + channels);
      this.logIndent(1, 'auth:' + auth);
      this.logIndent(1, 'initial resolution: ' + resolution);
    } else if (cname == 'transport') {
      // The 'transport' node is currently empty.
      var transport_children = content_child.childNodes;
      if (transport_children.length != 0) {
        return false;
      }
    } else {
      return false;
    }
  }
  return true;
};

/**
 * Pretty print the session-terminate info from the given Xml node.
 *
 * @param {Node} jingle Xml node with jingle session-terminate info contained in
 *                      child nodes.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettySessionTerminate = function(jingle) {
  if (jingle.childNodes.length != 1) {
    return false;
  }
  var reason = jingle.firstChild;
  if (reason.nodeName != 'reason' || reason.childNodes.length != 1) {
    return false;
  }
  var info = reason.firstChild;
  if (info.nodeName == 'success') {
    this.logIndent(1, 'reason=success');
  } else {
    return false;
  }
  return true;
};

/**
 * Pretty print the transport-info info from the given Xml node.
 *
 * @param {Node} jingle Xml node with jingle transport info contained in child
 *                      nodes.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettyTransportInfo = function(jingle) {
  if (jingle.childNodes.length != 1) {
    return false;
  }
  var content = jingle.firstChild;
  if (content.nodeName != 'content') {
    return false;
  }
  var transport = content.firstChild;
  if (transport.nodeName != 'transport') {
    return false;
  }
  var transport_children = transport.childNodes;
  for (var t = 0; t < transport_children.length; t++) {
    /** @type {Node} */
    var candidate = transport_children[t];
    if (candidate.nodeName != 'candidate') {
      return false;
    }
    var name = candidate.getAttribute('name');
    var address = candidate.getAttribute('address');
    var port = candidate.getAttribute('port');
    var pref = candidate.getAttribute('preference');
    var username = candidate.getAttribute('username');
    var protocol = candidate.getAttribute('protocol');
    var generation = candidate.getAttribute('generation');
    var password = candidate.getAttribute('password');
    var type = candidate.getAttribute('type');
    var network = candidate.getAttribute('network');

    var info = name + ': ' + address + ':' + port + ' ' + protocol +
        ' name:' + username + ' pwd:' + password +
        ' pref:' + pref +
        ' ' + type;
    if (network) {
      info = info + " network:'" + network + "'";
    }
    this.logIndent(1, info)
  }
  return true;
};

/**
 * Pretty print the jingle action contained in the given Xml node.
 *
 * @param {Node} jingle Xml node with jingle action contained in child nodes.
 * @param {string} action String containing the jingle action.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettyJingleAction = function(jingle, action) {
  if (action == 'session-initiate' || action == 'session-accept') {
    return this.prettySessionInitiateAccept(jingle);
  }
  if (action == 'session-terminate') {
    return this.prettySessionTerminate(jingle);
  }
  if (action == 'transport-info') {
    return this.prettyTransportInfo(jingle);
  }
  return false;
};

/**
 * Pretty print the jingle error information contained in the given Xml node.
 *
 * @param {Node} error Xml node containing error information in child nodes.
 *
 * @return {boolean} True if we were able to pretty-print the information.
 */
remoting.DebugLog.prototype.prettyError = function(error) {
  var code = error.getAttribute('code');
  var type = error.getAttribute('type');
  var hostname = error.getAttribute('err:hostname');
  var bnsname = error.getAttribute('err:bnsname');
  var stacktrace = error.getAttribute('err:stacktrace');
  this.logIndent(1, 'error ' + code + ' ' + type + " hostname:'" +
                  hostname + "' bnsname:'" + bnsname + "'");
  var children = error.childNodes;
  for (var i = 0; i < children.length; i++) {
    /** @type {Node} */
    var child = children[i];
    this.logIndent(1, child.nodeName);
  }
  if (stacktrace) {
    var stack = stacktrace.split(' | ');
    this.logIndent(1, 'stacktrace:');
    // We use 'length-1' because the stack trace ends with " | " which results
    // in an empty string at the end after the split.
    for (var s = 0; s < stack.length - 1; s++) {
      this.logIndent(2, stack[s]);
    }
  }
  return true;
};

/**
 * Print out the heading line for an iq node.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {string} id Packet id.
 * @param {string} desc Description of iq action for this node.
 * @param {string|null} sid Session id.
 */
remoting.DebugLog.prototype.prettyIqHeading = function(send, id, desc, sid) {
  var dir = (send ? 'send' : 'receive');
  var message = 'iq ' + dir + ' id=' + id;
  if (desc) {
    message = message + ' ' + desc;
  }
  if (sid) {
    message = message + ' sid=' + sid;
  }
  this.log(message);
}

/**
 * Print out an iq 'result'-type node.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {NodeList} iq_list Node list containing the 'result' xml.
 *
 * @return {boolean} True if the data was logged successfully.
 */
remoting.DebugLog.prototype.prettyIqResult = function(send, iq_list) {
  /** @type {Node} */
  var iq = iq_list[0];
  var id = iq.getAttribute('id');
  var iq_children = iq.childNodes;

  if (iq_children.length == 0) {
    this.prettyIqHeading(send, id, 'result (empty)', null);
    return true;
  } else if (iq_children.length == 1) {
    /** @type {Node} */
    var query = iq_children[0];
    if (query.nodeName != 'query') {
      return false;
    }
    var xmlns = query.getAttribute('xmlns');
    if (xmlns == 'google:jingleinfo') {
      this.prettyIqHeading(send, id, 'result ' + xmlns, null);
      return this.prettyJingleinfo(query);
    }
  }
  return false;
}

/**
 * Print out an iq 'get'-type node.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {NodeList} iq_list Node containing the 'get' xml.
 *
 * @return {boolean} True if the data was logged successfully.
 */
remoting.DebugLog.prototype.prettyIqGet = function(send, iq_list) {
  /** @type {Node} */
  var iq = iq_list[0];
  var id = iq.getAttribute('id');
  var iq_children = iq.childNodes;

  if (iq_children.length != 1) {
    return false;
  }
  /** @type {Node} */
  var query = iq_children[0];
  if (query.nodeName != 'query') {
    return false;
  }
  var xmlns = query.getAttribute('xmlns');
  this.prettyIqHeading(send, id, 'get ' + xmlns, null);
  return true;
}

/**
 * Print out an iq 'set'-type node.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {NodeList} iq_list Node containing the 'set' xml.
 *
 * @return {boolean} True if the data was logged successfully.
 */
remoting.DebugLog.prototype.prettyIqSet = function(send, iq_list) {
  /** @type {Node} */
  var iq = iq_list[0];
  var id = iq.getAttribute('id');
  var iq_children = iq.childNodes;

  var children = iq_children.length;
  if (children >= 1) {
    /** @type {Node} */
    var jingle = iq_children[0];
    if (jingle.nodeName != 'jingle') {
      return false;
    }
    var action = jingle.getAttribute('action');
    var sid = jingle.getAttribute('sid');

    if (children == 1) {
      this.prettyIqHeading(send, id, 'set ' + action, sid);
      return this.prettyJingleAction(jingle, action);

    } else if (children == 2) {
      if (action == 'session-initiate') {
        var sid = jingle.getAttribute('sid');
        this.prettyIqHeading(send, id, 'set ' + action, sid);
        if (!this.prettySessionInitiateAccept(jingle)) {
          return false;
        }

        // When there are two child nodes for a 'session-initiate' node,
        // the second is a duplicate  copy of the 'session' info added by
        // libjingle for backward compatability with an older version of
        // Jingle (called Gingle).
        // Since M16 we no longer use libjingle on the client side and thus
        // we no longer generate this duplicate node.

        // Require that second child is 'session' with type='initiate'.
        /** @type {Node} */
        var session = iq_children[1];
        if (session.nodeName != 'session') {
          return false;
        }
        var type = session.getAttribute('type');
        if (type != 'initiate') {
          return false;
        }
        // Silently ignore contents of 'session' node.
        return true;
      }
    }
  }
  return false;
}

/**
 * Print out an iq 'error'-type node.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {NodeList} iq_list Node containing the 'error' xml.
 *
 * @return {boolean} True if the data was logged successfully.
 */
remoting.DebugLog.prototype.prettyIqError = function(send, iq_list) {
  /** @type {Node} */
  var iq = iq_list[0];
  var id = iq.getAttribute('id');
  var iq_children = iq.childNodes;

  var children = iq_children.length;
  if (children != 2) {
    return false;
  }

  /** @type {Node} */
  var jingle = iq_children[0];
  if (jingle.nodeName != 'jingle') {
    return false;
  }
  var action = jingle.getAttribute('action');
  var sid = jingle.getAttribute('sid');
  this.prettyIqHeading(send, id, 'error from ' + action, sid);
  if (!this.prettyJingleAction(jingle, action)) {
    return false;
  }
  /** @type {Node} */
  var error = iq_children[1];
  if (error.nodeName != 'cli:error') {
    return false;
  }
  return this.prettyError(error);
}

/**
 * Try to log a pretty-print the given IQ stanza (XML).
 * Return true if the stanza was successfully printed.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {string} message The XML stanza to add to the log.
 *
 * @return {boolean} True if the stanza was logged.
 */
remoting.DebugLog.prototype.prettyIq = function(send, message) {
  var parser = new DOMParser();
  var xml = parser.parseFromString(message, 'text/xml');

  var iq_list = xml.getElementsByTagName('iq');

  if (iq_list && iq_list.length > 0) {
    /** @type {Node} */
    var iq = iq_list[0];
    // Verify that the to/from fields match the expected sender/receiver.
    var to = iq.getAttribute('to');
    var from = iq.getAttribute('from');
    if (send) {
      if (to && to != this.hostJid)
        return false;
      if (from && from != this.clientJid)
        return false;
    } else {
      if (to && to != this.clientJid)
        return false;
      if (from && from != this.hostJid)
        return false;
    }

    var type = iq.getAttribute('type');
    if (type == 'result') {
      return this.prettyIqResult(send, iq_list);
    } else if (type == 'get') {
      return this.prettyIqGet(send, iq_list);
    } else if (type == 'set') {
      return this.prettyIqSet(send, iq_list);
    } else  if (type == 'error') {
      return this.prettyIqError(send, iq_list);
    }
  }

  return false;
};

/**
 * Add the given IQ stanza to the debug log.
 * When possible, the stanza string will be simplified to make it more
 * readable.
 *
 * @param {boolean} send True if we're sending this stanza; false for receiving.
 * @param {string} message The XML stanza to add to the log.
 */
remoting.DebugLog.prototype.logIq = function(send, message) {
  if (!this.prettyIq(send, message)) {
    // Fall back to showing the raw stanza.
    var prefix = (send ? 'Sending Iq: ' : 'Receiving Iq: ');
    this.log(prefix + message);
  }
};

/** @type {remoting.DebugLog} */
remoting.debug = null;
