// Copyright 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/chromeos/file_system_provider/operations/unobserve_entry.h"

#include <string>

#include "chrome/common/extensions/api/file_system_provider.h"
#include "chrome/common/extensions/api/file_system_provider_internal.h"

namespace chromeos {
namespace file_system_provider {
namespace operations {

UnobserveEntry::UnobserveEntry(
    extensions::EventRouter* event_router,
    const ProvidedFileSystemInfo& file_system_info,
    const base::FilePath& entry_path,
    const storage::AsyncFileUtil::StatusCallback& callback)
    : Operation(event_router, file_system_info),
      entry_path_(entry_path),
      callback_(callback) {
}

UnobserveEntry::~UnobserveEntry() {
}

bool UnobserveEntry::Execute(int request_id) {
  using extensions::api::file_system_provider::UnobserveEntryRequestedOptions;

  UnobserveEntryRequestedOptions options;
  options.file_system_id = file_system_info_.file_system_id();
  options.request_id = request_id;
  options.entry_path = entry_path_.AsUTF8Unsafe();

  return SendEvent(
      request_id,
      extensions::api::file_system_provider::OnUnobserveEntryRequested::
          kEventName,
      extensions::api::file_system_provider::OnUnobserveEntryRequested::Create(
          options));
}

void UnobserveEntry::OnSuccess(int /* request_id */,
                               scoped_ptr<RequestValue> /* result */,
                               bool has_more) {
  callback_.Run(base::File::FILE_OK);
}

void UnobserveEntry::OnError(int /* request_id */,
                             scoped_ptr<RequestValue> /* result */,
                             base::File::Error error) {
  callback_.Run(error);
}

}  // namespace operations
}  // namespace file_system_provider
}  // namespace chromeos