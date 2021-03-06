// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef MOJO_SYSTEM_CORE_H_
#define MOJO_SYSTEM_CORE_H_

#include <stdint.h>

#include "base/macros.h"
#include "base/memory/ref_counted.h"
#include "base/synchronization/lock.h"
#include "mojo/public/c/system/buffer.h"
#include "mojo/public/c/system/data_pipe.h"
#include "mojo/public/c/system/message_pipe.h"
#include "mojo/public/c/system/types.h"
#include "mojo/system/handle_table.h"
#include "mojo/system/mapping_table.h"
#include "mojo/system/memory.h"
#include "mojo/system/system_impl_export.h"

namespace mojo {
namespace system {

class Dispatcher;
struct HandleSignalsState;

// |Core| is an object that implements the Mojo system calls. All public methods
// are thread-safe.
class MOJO_SYSTEM_IMPL_EXPORT Core {
 public:
  // These methods are only to be used by via the embedder API (and internally).
  Core();
  virtual ~Core();

  // Adds |dispatcher| to the handle table, returning the handle for it. Returns
  // |MOJO_HANDLE_INVALID| on failure, namely if the handle table is full.
  MojoHandle AddDispatcher(const scoped_refptr<Dispatcher>& dispatcher);

  // Looks up the dispatcher for the given handle. Returns null if the handle is
  // invalid.
  scoped_refptr<Dispatcher> GetDispatcher(MojoHandle handle);

  // System calls implementation.
  MojoTimeTicks GetTimeTicksNow();
  MojoResult Close(MojoHandle handle);
  MojoResult Wait(MojoHandle handle,
                  MojoHandleSignals signals,
                  MojoDeadline deadline,
                  UserPointer<MojoHandleSignalsState> signals_state);
  MojoResult WaitMany(UserPointer<const MojoHandle> handles,
                      UserPointer<const MojoHandleSignals> signals,
                      uint32_t num_handles,
                      MojoDeadline deadline,
                      UserPointer<uint32_t> result_index,
                      UserPointer<MojoHandleSignalsState> signals_states);
  MojoResult CreateMessagePipe(
      UserPointer<const MojoCreateMessagePipeOptions> options,
      UserPointer<MojoHandle> message_pipe_handle0,
      UserPointer<MojoHandle> message_pipe_handle1);
  MojoResult WriteMessage(MojoHandle message_pipe_handle,
                          UserPointer<const void> bytes,
                          uint32_t num_bytes,
                          UserPointer<const MojoHandle> handles,
                          uint32_t num_handles,
                          MojoWriteMessageFlags flags);
  MojoResult ReadMessage(MojoHandle message_pipe_handle,
                         UserPointer<void> bytes,
                         UserPointer<uint32_t> num_bytes,
                         UserPointer<MojoHandle> handles,
                         UserPointer<uint32_t> num_handles,
                         MojoReadMessageFlags flags);
  MojoResult CreateDataPipe(
      UserPointer<const MojoCreateDataPipeOptions> options,
      UserPointer<MojoHandle> data_pipe_producer_handle,
      UserPointer<MojoHandle> data_pipe_consumer_handle);
  MojoResult WriteData(MojoHandle data_pipe_producer_handle,
                       UserPointer<const void> elements,
                       UserPointer<uint32_t> num_bytes,
                       MojoWriteDataFlags flags);
  MojoResult BeginWriteData(MojoHandle data_pipe_producer_handle,
                            UserPointer<void*> buffer,
                            UserPointer<uint32_t> buffer_num_bytes,
                            MojoWriteDataFlags flags);
  MojoResult EndWriteData(MojoHandle data_pipe_producer_handle,
                          uint32_t num_bytes_written);
  MojoResult ReadData(MojoHandle data_pipe_consumer_handle,
                      UserPointer<void> elements,
                      UserPointer<uint32_t> num_bytes,
                      MojoReadDataFlags flags);
  MojoResult BeginReadData(MojoHandle data_pipe_consumer_handle,
                           UserPointer<const void*> buffer,
                           UserPointer<uint32_t> buffer_num_bytes,
                           MojoReadDataFlags flags);
  MojoResult EndReadData(MojoHandle data_pipe_consumer_handle,
                         uint32_t num_bytes_read);
  MojoResult CreateSharedBuffer(
      UserPointer<const MojoCreateSharedBufferOptions> options,
      uint64_t num_bytes,
      UserPointer<MojoHandle> shared_buffer_handle);
  MojoResult DuplicateBufferHandle(
      MojoHandle buffer_handle,
      UserPointer<const MojoDuplicateBufferHandleOptions> options,
      UserPointer<MojoHandle> new_buffer_handle);
  MojoResult MapBuffer(MojoHandle buffer_handle,
                       uint64_t offset,
                       uint64_t num_bytes,
                       UserPointer<void*> buffer,
                       MojoMapBufferFlags flags);
  MojoResult UnmapBuffer(UserPointer<void> buffer);

 private:
  friend bool internal::ShutdownCheckNoLeaks(Core*);

  // Internal implementation of |Wait()| and |WaitMany()|; doesn't do basic
  // validation of arguments. |*result_index| is only set if the result (whether
  // success or failure) applies to a specific handle, so its value should be
  // preinitialized to |static_cast<uint32_t>(-1)|.
  MojoResult WaitManyInternal(const MojoHandle* handles,
                              const MojoHandleSignals* signals,
                              uint32_t num_handles,
                              MojoDeadline deadline,
                              uint32_t* result_index,
                              HandleSignalsState* signals_states);

  // ---------------------------------------------------------------------------

  // TODO(vtl): |handle_table_lock_| should be a reader-writer lock (if only we
  // had them).
  base::Lock handle_table_lock_;  // Protects |handle_table_|.
  HandleTable handle_table_;

  base::Lock mapping_table_lock_;  // Protects |mapping_table_|.
  MappingTable mapping_table_;

  // ---------------------------------------------------------------------------

  DISALLOW_COPY_AND_ASSIGN(Core);
};

}  // namespace system
}  // namespace mojo

#endif  // MOJO_SYSTEM_CORE_H_
