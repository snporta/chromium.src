// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "content/browser/renderer_host/media/audio_input_sync_writer.h"

#include <algorithm>

#if defined(OS_ANDROID)
#include "base/android/jni_android.h"
#endif
#include "base/memory/shared_memory.h"
#include "content/browser/renderer_host/media/media_stream_manager.h"

static const uint32 kLogDelayThreadholdMs = 500;

namespace content {

AudioInputSyncWriter::AudioInputSyncWriter(
    base::SharedMemory* shared_memory,
    int shared_memory_segment_count)
    : shared_memory_(shared_memory),
      shared_memory_segment_count_(shared_memory_segment_count),
      current_segment_id_(0),
      creation_time_(base::Time::Now()) {
  DCHECK_GT(shared_memory_segment_count, 0);
  DCHECK_EQ(shared_memory->requested_size() % shared_memory_segment_count, 0u);
  shared_memory_segment_size_ =
      shared_memory->requested_size() / shared_memory_segment_count;
}

AudioInputSyncWriter::~AudioInputSyncWriter() {}

// TODO(henrika): Combine into one method (including Write).
void AudioInputSyncWriter::UpdateRecordedBytes(uint32 bytes) {
  socket_->Send(&bytes, sizeof(bytes));
}

uint32 AudioInputSyncWriter::Write(const void* data,
                                   uint32 size,
                                   double volume,
                                   bool key_pressed) {
  std::ostringstream oss;
  if (last_write_time_.is_null()) {
    // This is the first time Write is called.
    base::TimeDelta interval = base::Time::Now() - creation_time_;
    oss << "Audio input data received for the first time: delay = "
        << interval.InMilliseconds() << "ms.";
  } else {
    base::TimeDelta interval = base::Time::Now() - last_write_time_;
    if (interval.InMilliseconds() > kLogDelayThreadholdMs) {
      oss << "Audio input data delay unexpectedly long: delay = "
         << interval.InMilliseconds() << "ms.";
    }
  }
  if (!oss.str().empty()) {
    MediaStreamManager::SendMessageToNativeLog(oss.str());

    // MediaStreamManager::SendMessageToNativeLog posts a task to the UI thread,
    // which will attach the audio thread to the Android java VM. Unlike chrome
    // created threads, the audio thread is owned by the OS and does not detach
    // itself from the VM on exit, causing a crash (crbug/365915). So we detach
    // here to make sure the thread exits clean.
#if defined(OS_ANDROID)
    base::android::DetachFromVM();
#endif
  }

  last_write_time_ = base::Time::Now();

  uint8* ptr = static_cast<uint8*>(shared_memory_->memory());
  ptr += current_segment_id_ * shared_memory_segment_size_;
  media::AudioInputBuffer* buffer =
      reinterpret_cast<media::AudioInputBuffer*>(ptr);
  buffer->params.volume = volume;
  buffer->params.size = size;
  buffer->params.key_pressed = key_pressed;
  memcpy(buffer->audio, data, size);

  if (++current_segment_id_ >= shared_memory_segment_count_)
    current_segment_id_ = 0;

  return size;
}

void AudioInputSyncWriter::Close() {
  socket_->Close();
}

bool AudioInputSyncWriter::Init() {
  socket_.reset(new base::CancelableSyncSocket());
  foreign_socket_.reset(new base::CancelableSyncSocket());
  return base::CancelableSyncSocket::CreatePair(socket_.get(),
                                                foreign_socket_.get());
}

#if defined(OS_WIN)

bool AudioInputSyncWriter::PrepareForeignSocketHandle(
    base::ProcessHandle process_handle,
    base::SyncSocket::Handle* foreign_handle) {
  ::DuplicateHandle(GetCurrentProcess(), foreign_socket_->handle(),
                    process_handle, foreign_handle,
                    0, FALSE, DUPLICATE_SAME_ACCESS);
  return (*foreign_handle != 0);
}

#else

bool AudioInputSyncWriter::PrepareForeignSocketHandle(
    base::ProcessHandle process_handle,
    base::FileDescriptor* foreign_handle) {
  foreign_handle->fd = foreign_socket_->handle();
  foreign_handle->auto_close = false;
  return (foreign_handle->fd != -1);
}

#endif

}  // namespace content
