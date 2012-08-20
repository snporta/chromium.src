// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "sync/internal_api/public/sync_encryption_handler.h"

namespace syncer {

SyncEncryptionHandler::Observer::Observer() {}
SyncEncryptionHandler::Observer::~Observer() {}

SyncEncryptionHandler::SyncEncryptionHandler() {}
SyncEncryptionHandler::~SyncEncryptionHandler() {}

// Static.
ModelTypeSet SyncEncryptionHandler::SensitiveTypes() {
  // Both of these have their own encryption schemes, but we include them
  // anyways.
  ModelTypeSet types;
  types.Put(PASSWORDS);
  types.Put(NIGORI);
  return types;
}

}  // namespace syncer
