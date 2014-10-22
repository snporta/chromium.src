# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Top-level presubmit script for Chromium.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts
for more details about the presubmit API built into gcl.
"""


_EXCLUDED_PATHS = (
    r"^breakpad[\\\/].*",
    r"^native_client_sdk[\\\/]src[\\\/]build_tools[\\\/]make_rules.py",
    r"^native_client_sdk[\\\/]src[\\\/]build_tools[\\\/]make_simple.py",
    r"^native_client_sdk[\\\/]src[\\\/]tools[\\\/].*.mk",
    r"^net[\\\/]tools[\\\/]spdyshark[\\\/].*",
    r"^skia[\\\/].*",
    r"^v8[\\\/].*",
    r".*MakeFile$",
    r".+_autogen\.h$",
    r".+[\\\/]pnacl_shim\.c$",
    r"^gpu[\\\/]config[\\\/].*_list_json\.cc$",
    r"^chrome[\\\/]browser[\\\/]resources[\\\/]pdf[\\\/]index.js"
)

# The NetscapePlugIn library is excluded from pan-project as it will soon
# be deleted together with the rest of the NPAPI and it's not worthwhile to
# update the coding style until then.
_TESTRUNNER_PATHS = (
    r"^content[\\\/]shell[\\\/]tools[\\\/]plugin[\\\/].*",
)

# Fragment of a regular expression that matches C++ and Objective-C++
# implementation files.
_IMPLEMENTATION_EXTENSIONS = r'\.(cc|cpp|cxx|mm)$'

# Regular expression that matches code only used for test binaries
# (best effort).
_TEST_CODE_EXCLUDED_PATHS = (
    r'.*[\\\/](fake_|test_|mock_).+%s' % _IMPLEMENTATION_EXTENSIONS,
    r'.+_test_(base|support|util)%s' % _IMPLEMENTATION_EXTENSIONS,
    r'.+_(api|browser|kif|perf|pixel|unit|ui)?test(_[a-z]+)?%s' %
        _IMPLEMENTATION_EXTENSIONS,
    r'.+profile_sync_service_harness%s' % _IMPLEMENTATION_EXTENSIONS,
    r'.*[\\\/](test|tool(s)?)[\\\/].*',
    # content_shell is used for running layout tests.
    r'content[\\\/]shell[\\\/].*',
    # At request of folks maintaining this folder.
    r'chrome[\\\/]browser[\\\/]automation[\\\/].*',
    # Non-production example code.
    r'mojo[\\\/]examples[\\\/].*',
    # Launcher for running iOS tests on the simulator.
    r'testing[\\\/]iossim[\\\/]iossim\.mm$',
)

_TEST_ONLY_WARNING = (
    'You might be calling functions intended only for testing from\n'
    'production code.  It is OK to ignore this warning if you know what\n'
    'you are doing, as the heuristics used to detect the situation are\n'
    'not perfect.  The commit queue will not block on this warning.')


_INCLUDE_ORDER_WARNING = (
    'Your #include order seems to be broken. Send mail to\n'
    'marja@chromium.org if this is not the case.')


_BANNED_OBJC_FUNCTIONS = (
    (
      'addTrackingRect:',
      (
       'The use of -[NSView addTrackingRect:owner:userData:assumeInside:] is'
       'prohibited. Please use CrTrackingArea instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      False,
    ),
    (
      r'/NSTrackingArea\W',
      (
       'The use of NSTrackingAreas is prohibited. Please use CrTrackingArea',
       'instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      False,
    ),
    (
      'convertPointFromBase:',
      (
       'The use of -[NSView convertPointFromBase:] is almost certainly wrong.',
       'Please use |convertPoint:(point) fromView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
    (
      'convertPointToBase:',
      (
       'The use of -[NSView convertPointToBase:] is almost certainly wrong.',
       'Please use |convertPoint:(point) toView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
    (
      'convertRectFromBase:',
      (
       'The use of -[NSView convertRectFromBase:] is almost certainly wrong.',
       'Please use |convertRect:(point) fromView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
    (
      'convertRectToBase:',
      (
       'The use of -[NSView convertRectToBase:] is almost certainly wrong.',
       'Please use |convertRect:(point) toView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
    (
      'convertSizeFromBase:',
      (
       'The use of -[NSView convertSizeFromBase:] is almost certainly wrong.',
       'Please use |convertSize:(point) fromView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
    (
      'convertSizeToBase:',
      (
       'The use of -[NSView convertSizeToBase:] is almost certainly wrong.',
       'Please use |convertSize:(point) toView:nil| instead.',
       'http://dev.chromium.org/developers/coding-style/cocoa-dos-and-donts',
      ),
      True,
    ),
)


_BANNED_CPP_FUNCTIONS = (
    # Make sure that gtest's FRIEND_TEST() macro is not used; the
    # FRIEND_TEST_ALL_PREFIXES() macro from base/gtest_prod_util.h should be
    # used instead since that allows for FLAKY_ and DISABLED_ prefixes.
    (
      'FRIEND_TEST(',
      (
       'Chromium code should not use gtest\'s FRIEND_TEST() macro. Include',
       'base/gtest_prod_util.h and use FRIEND_TEST_ALL_PREFIXES() instead.',
      ),
      False,
      (),
    ),
    (
      'ScopedAllowIO',
      (
       'New code should not use ScopedAllowIO. Post a task to the blocking',
       'pool or the FILE thread instead.',
      ),
      True,
      (
        r"^base[\\\/]process[\\\/]process_metrics_linux\.cc$",
        r"^chrome[\\\/]browser[\\\/]chromeos[\\\/]boot_times_loader\.cc$",
        r"^components[\\\/]crash[\\\/]app[\\\/]breakpad_mac\.mm$",
        r"^content[\\\/]shell[\\\/]browser[\\\/]shell_browser_main\.cc$",
        r"^content[\\\/]shell[\\\/]browser[\\\/]shell_message_filter\.cc$",
        r"^mojo[\\\/]edk[\\\/]embedder[\\\/]" +
            r"simple_platform_shared_buffer_posix\.cc$",
        r"^net[\\\/]disk_cache[\\\/]cache_util\.cc$",
        r"^net[\\\/]url_request[\\\/]test_url_fetcher_factory\.cc$",
      ),
    ),
    (
      'SkRefPtr',
      (
        'The use of SkRefPtr is prohibited. ',
        'Please use skia::RefPtr instead.'
      ),
      True,
      (),
    ),
    (
      'SkAutoRef',
      (
        'The indirect use of SkRefPtr via SkAutoRef is prohibited. ',
        'Please use skia::RefPtr instead.'
      ),
      True,
      (),
    ),
    (
      'SkAutoTUnref',
      (
        'The use of SkAutoTUnref is dangerous because it implicitly ',
        'converts to a raw pointer. Please use skia::RefPtr instead.'
      ),
      True,
      (),
    ),
    (
      'SkAutoUnref',
      (
        'The indirect use of SkAutoTUnref through SkAutoUnref is dangerous ',
        'because it implicitly converts to a raw pointer. ',
        'Please use skia::RefPtr instead.'
      ),
      True,
      (),
    ),
    (
      r'/HANDLE_EINTR\(.*close',
      (
       'HANDLE_EINTR(close) is invalid. If close fails with EINTR, the file',
       'descriptor will be closed, and it is incorrect to retry the close.',
       'Either call close directly and ignore its return value, or wrap close',
       'in IGNORE_EINTR to use its return value. See http://crbug.com/269623'
      ),
      True,
      (),
    ),
    (
      r'/IGNORE_EINTR\((?!.*close)',
      (
       'IGNORE_EINTR is only valid when wrapping close. To wrap other system',
       'calls, use HANDLE_EINTR. See http://crbug.com/269623',
      ),
      True,
      (
        # Files that #define IGNORE_EINTR.
        r'^base[\\\/]posix[\\\/]eintr_wrapper\.h$',
        r'^ppapi[\\\/]tests[\\\/]test_broker\.cc$',
      ),
    ),
    (
      r'/v8::Extension\(',
      (
        'Do not introduce new v8::Extensions into the code base, use',
        'gin::Wrappable instead. See http://crbug.com/334679',
      ),
      True,
      (
        r'extensions[\\\/]renderer[\\\/]safe_builtins\.*',
      ),
    ),
)

_IPC_ENUM_TRAITS_DEPRECATED = (
    'You are using IPC_ENUM_TRAITS() in your code. It has been deprecated.\n'
    'See http://www.chromium.org/Home/chromium-security/education/security-tips-for-ipc')


_VALID_OS_MACROS = (
    # Please keep sorted.
    'OS_ANDROID',
    'OS_ANDROID_HOST',
    'OS_BSD',
    'OS_CAT',       # For testing.
    'OS_CHROMEOS',
    'OS_FREEBSD',
    'OS_IOS',
    'OS_LINUX',
    'OS_MACOSX',
    'OS_NACL',
    'OS_OPENBSD',
    'OS_POSIX',
    'OS_QNX',
    'OS_SOLARIS',
    'OS_WIN',
)


def _CheckNoProductionCodeUsingTestOnlyFunctions(input_api, output_api):
  """Attempts to prevent use of functions intended only for testing in
  non-testing code. For now this is just a best-effort implementation
  that ignores header files and may have some false positives. A
  better implementation would probably need a proper C++ parser.
  """
  # We only scan .cc files and the like, as the declaration of
  # for-testing functions in header files are hard to distinguish from
  # calls to such functions without a proper C++ parser.
  file_inclusion_pattern = r'.+%s' % _IMPLEMENTATION_EXTENSIONS

  base_function_pattern = r'[ :]test::[^\s]+|ForTest(ing)?|for_test(ing)?'
  inclusion_pattern = input_api.re.compile(r'(%s)\s*\(' % base_function_pattern)
  comment_pattern = input_api.re.compile(r'//.*(%s)' % base_function_pattern)
  exclusion_pattern = input_api.re.compile(
    r'::[A-Za-z0-9_]+(%s)|(%s)[^;]+\{' % (
      base_function_pattern, base_function_pattern))

  def FilterFile(affected_file):
    black_list = (_EXCLUDED_PATHS +
                  _TEST_CODE_EXCLUDED_PATHS +
                  input_api.DEFAULT_BLACK_LIST)
    return input_api.FilterSourceFile(
      affected_file,
      white_list=(file_inclusion_pattern, ),
      black_list=black_list)

  problems = []
  for f in input_api.AffectedSourceFiles(FilterFile):
    local_path = f.LocalPath()
    for line_number, line in f.ChangedContents():
      if (inclusion_pattern.search(line) and
          not comment_pattern.search(line) and
          not exclusion_pattern.search(line)):
        problems.append(
          '%s:%d\n    %s' % (local_path, line_number, line.strip()))

  if problems:
    return [output_api.PresubmitPromptOrNotify(_TEST_ONLY_WARNING, problems)]
  else:
    return []


def _CheckNoIOStreamInHeaders(input_api, output_api):
  """Checks to make sure no .h files include <iostream>."""
  files = []
  pattern = input_api.re.compile(r'^#include\s*<iostream>',
                                 input_api.re.MULTILINE)
  for f in input_api.AffectedSourceFiles(input_api.FilterSourceFile):
    if not f.LocalPath().endswith('.h'):
      continue
    contents = input_api.ReadFile(f)
    if pattern.search(contents):
      files.append(f)

  if len(files):
    return [ output_api.PresubmitError(
        'Do not #include <iostream> in header files, since it inserts static '
        'initialization into every file including the header. Instead, '
        '#include <ostream>. See http://crbug.com/94794',
        files) ]
  return []


def _CheckNoUNIT_TESTInSourceFiles(input_api, output_api):
  """Checks to make sure no source files use UNIT_TEST"""
  problems = []
  for f in input_api.AffectedFiles():
    if (not f.LocalPath().endswith(('.cc', '.mm'))):
      continue

    for line_num, line in f.ChangedContents():
      if 'UNIT_TEST ' in line or line.endswith('UNIT_TEST'):
        problems.append('    %s:%d' % (f.LocalPath(), line_num))

  if not problems:
    return []
  return [output_api.PresubmitPromptWarning('UNIT_TEST is only for headers.\n' +
      '\n'.join(problems))]


def _CheckNoNewWStrings(input_api, output_api):
  """Checks to make sure we don't introduce use of wstrings."""
  problems = []
  for f in input_api.AffectedFiles():
    if (not f.LocalPath().endswith(('.cc', '.h')) or
        f.LocalPath().endswith(('test.cc', '_win.cc', '_win.h'))):
      continue

    allowWString = False
    for line_num, line in f.ChangedContents():
      if 'presubmit: allow wstring' in line:
        allowWString = True
      elif not allowWString and 'wstring' in line:
        problems.append('    %s:%d' % (f.LocalPath(), line_num))
        allowWString = False
      else:
        allowWString = False

  if not problems:
    return []
  return [output_api.PresubmitPromptWarning('New code should not use wstrings.'
      '  If you are calling a cross-platform API that accepts a wstring, '
      'fix the API.\n' +
      '\n'.join(problems))]


def _CheckNoDEPSGIT(input_api, output_api):
  """Make sure .DEPS.git is never modified manually."""
  if any(f.LocalPath().endswith('.DEPS.git') for f in
      input_api.AffectedFiles()):
    return [output_api.PresubmitError(
      'Never commit changes to .DEPS.git. This file is maintained by an\n'
      'automated system based on what\'s in DEPS and your changes will be\n'
      'overwritten.\n'
      'See https://sites.google.com/a/chromium.org/dev/developers/how-tos/get-the-code#Rolling_DEPS\n'
      'for more information')]
  return []


def _CheckValidHostsInDEPS(input_api, output_api):
  """Checks that DEPS file deps are from allowed_hosts."""
  # Run only if DEPS file has been modified to annoy fewer bystanders.
  if all(f.LocalPath() != 'DEPS' for f in input_api.AffectedFiles()):
    return []
  # Outsource work to gclient verify
  try:
    input_api.subprocess.check_output(['gclient', 'verify'])
    return []
  except input_api.subprocess.CalledProcessError, error:
    return [output_api.PresubmitError(
        'DEPS file must have only git dependencies.',
        long_text=error.output)]


def _CheckNoBannedFunctions(input_api, output_api):
  """Make sure that banned functions are not used."""
  warnings = []
  errors = []

  file_filter = lambda f: f.LocalPath().endswith(('.mm', '.m', '.h'))
  for f in input_api.AffectedFiles(file_filter=file_filter):
    for line_num, line in f.ChangedContents():
      for func_name, message, error in _BANNED_OBJC_FUNCTIONS:
        matched = False
        if func_name[0:1] == '/':
          regex = func_name[1:]
          if input_api.re.search(regex, line):
            matched = True
        elif func_name in line:
            matched = True
        if matched:
          problems = warnings;
          if error:
            problems = errors;
          problems.append('    %s:%d:' % (f.LocalPath(), line_num))
          for message_line in message:
            problems.append('      %s' % message_line)

  file_filter = lambda f: f.LocalPath().endswith(('.cc', '.mm', '.h'))
  for f in input_api.AffectedFiles(file_filter=file_filter):
    for line_num, line in f.ChangedContents():
      for func_name, message, error, excluded_paths in _BANNED_CPP_FUNCTIONS:
        def IsBlacklisted(affected_file, blacklist):
          local_path = affected_file.LocalPath()
          for item in blacklist:
            if input_api.re.match(item, local_path):
              return True
          return False
        if IsBlacklisted(f, excluded_paths):
          continue
        matched = False
        if func_name[0:1] == '/':
          regex = func_name[1:]
          if input_api.re.search(regex, line):
            matched = True
        elif func_name in line:
            matched = True
        if matched:
          problems = warnings;
          if error:
            problems = errors;
          problems.append('    %s:%d:' % (f.LocalPath(), line_num))
          for message_line in message:
            problems.append('      %s' % message_line)

  result = []
  if (warnings):
    result.append(output_api.PresubmitPromptWarning(
        'Banned functions were used.\n' + '\n'.join(warnings)))
  if (errors):
    result.append(output_api.PresubmitError(
        'Banned functions were used.\n' + '\n'.join(errors)))
  return result


def _CheckNoPragmaOnce(input_api, output_api):
  """Make sure that banned functions are not used."""
  files = []
  pattern = input_api.re.compile(r'^#pragma\s+once',
                                 input_api.re.MULTILINE)
  for f in input_api.AffectedSourceFiles(input_api.FilterSourceFile):
    if not f.LocalPath().endswith('.h'):
      continue
    contents = input_api.ReadFile(f)
    if pattern.search(contents):
      files.append(f)

  if files:
    return [output_api.PresubmitError(
        'Do not use #pragma once in header files.\n'
        'See http://www.chromium.org/developers/coding-style#TOC-File-headers',
        files)]
  return []


def _CheckNoTrinaryTrueFalse(input_api, output_api):
  """Checks to make sure we don't introduce use of foo ? true : false."""
  problems = []
  pattern = input_api.re.compile(r'\?\s*(true|false)\s*:\s*(true|false)')
  for f in input_api.AffectedFiles():
    if not f.LocalPath().endswith(('.cc', '.h', '.inl', '.m', '.mm')):
      continue

    for line_num, line in f.ChangedContents():
      if pattern.match(line):
        problems.append('    %s:%d' % (f.LocalPath(), line_num))

  if not problems:
    return []
  return [output_api.PresubmitPromptWarning(
      'Please consider avoiding the "? true : false" pattern if possible.\n' +
      '\n'.join(problems))]


def _CheckUnwantedDependencies(input_api, output_api):
  """Runs checkdeps on #include statements added in this
  change. Breaking - rules is an error, breaking ! rules is a
  warning.
  """
  import sys
  # We need to wait until we have an input_api object and use this
  # roundabout construct to import checkdeps because this file is
  # eval-ed and thus doesn't have __file__.
  original_sys_path = sys.path
  try:
    sys.path = sys.path + [input_api.os_path.join(
        input_api.PresubmitLocalPath(), 'buildtools', 'checkdeps')]
    import checkdeps
    from cpp_checker import CppChecker
    from rules import Rule
  finally:
    # Restore sys.path to what it was before.
    sys.path = original_sys_path

  added_includes = []
  for f in input_api.AffectedFiles():
    if not CppChecker.IsCppFile(f.LocalPath()):
      continue

    changed_lines = [line for line_num, line in f.ChangedContents()]
    added_includes.append([f.LocalPath(), changed_lines])

  deps_checker = checkdeps.DepsChecker(input_api.PresubmitLocalPath())

  error_descriptions = []
  warning_descriptions = []
  for path, rule_type, rule_description in deps_checker.CheckAddedCppIncludes(
      added_includes):
    description_with_path = '%s\n    %s' % (path, rule_description)
    if rule_type == Rule.DISALLOW:
      error_descriptions.append(description_with_path)
    else:
      warning_descriptions.append(description_with_path)

  results = []
  if error_descriptions:
    results.append(output_api.PresubmitError(
        'You added one or more #includes that violate checkdeps rules.',
        error_descriptions))
  if warning_descriptions:
    results.append(output_api.PresubmitPromptOrNotify(
        'You added one or more #includes of files that are temporarily\n'
        'allowed but being removed. Can you avoid introducing the\n'
        '#include? See relevant DEPS file(s) for details and contacts.',
        warning_descriptions))
  return results


def _CheckFilePermissions(input_api, output_api):
  """Check that all files have their permissions properly set."""
  if input_api.platform == 'win32':
    return []
  args = [input_api.python_executable, 'tools/checkperms/checkperms.py',
          '--root', input_api.change.RepositoryRoot()]
  for f in input_api.AffectedFiles():
    args += ['--file', f.LocalPath()]
  checkperms = input_api.subprocess.Popen(args,
                                          stdout=input_api.subprocess.PIPE)
  errors = checkperms.communicate()[0].strip()
  if errors:
    return [output_api.PresubmitError('checkperms.py failed.',
                                      errors.splitlines())]
  return []


def _CheckNoAuraWindowPropertyHInHeaders(input_api, output_api):
  """Makes sure we don't include ui/aura/window_property.h
  in header files.
  """
  pattern = input_api.re.compile(r'^#include\s*"ui/aura/window_property.h"')
  errors = []
  for f in input_api.AffectedFiles():
    if not f.LocalPath().endswith('.h'):
      continue
    for line_num, line in f.ChangedContents():
      if pattern.match(line):
        errors.append('    %s:%d' % (f.LocalPath(), line_num))

  results = []
  if errors:
    results.append(output_api.PresubmitError(
      'Header files should not include ui/aura/window_property.h', errors))
  return results


def _CheckIncludeOrderForScope(scope, input_api, file_path, changed_linenums):
  """Checks that the lines in scope occur in the right order.

  1. C system files in alphabetical order
  2. C++ system files in alphabetical order
  3. Project's .h files
  """

  c_system_include_pattern = input_api.re.compile(r'\s*#include <.*\.h>')
  cpp_system_include_pattern = input_api.re.compile(r'\s*#include <.*>')
  custom_include_pattern = input_api.re.compile(r'\s*#include ".*')

  C_SYSTEM_INCLUDES, CPP_SYSTEM_INCLUDES, CUSTOM_INCLUDES = range(3)

  state = C_SYSTEM_INCLUDES

  previous_line = ''
  previous_line_num = 0
  problem_linenums = []
  for line_num, line in scope:
    if c_system_include_pattern.match(line):
      if state != C_SYSTEM_INCLUDES:
        problem_linenums.append((line_num, previous_line_num))
      elif previous_line and previous_line > line:
        problem_linenums.append((line_num, previous_line_num))
    elif cpp_system_include_pattern.match(line):
      if state == C_SYSTEM_INCLUDES:
        state = CPP_SYSTEM_INCLUDES
      elif state == CUSTOM_INCLUDES:
        problem_linenums.append((line_num, previous_line_num))
      elif previous_line and previous_line > line:
        problem_linenums.append((line_num, previous_line_num))
    elif custom_include_pattern.match(line):
      if state != CUSTOM_INCLUDES:
        state = CUSTOM_INCLUDES
      elif previous_line and previous_line > line:
        problem_linenums.append((line_num, previous_line_num))
    else:
      problem_linenums.append(line_num)
    previous_line = line
    previous_line_num = line_num

  warnings = []
  for (line_num, previous_line_num) in problem_linenums:
    if line_num in changed_linenums or previous_line_num in changed_linenums:
      warnings.append('    %s:%d' % (file_path, line_num))
  return warnings


def _CheckIncludeOrderInFile(input_api, f, changed_linenums):
  """Checks the #include order for the given file f."""

  system_include_pattern = input_api.re.compile(r'\s*#include \<.*')
  # Exclude the following includes from the check:
  # 1) #include <.../...>, e.g., <sys/...> includes often need to appear in a
  # specific order.
  # 2) <atlbase.h>, "build/build_config.h"
  excluded_include_pattern = input_api.re.compile(
      r'\s*#include (\<.*/.*|\<atlbase\.h\>|"build/build_config.h")')
  custom_include_pattern = input_api.re.compile(r'\s*#include "(?P<FILE>.*)"')
  # Match the final or penultimate token if it is xxxtest so we can ignore it
  # when considering the special first include.
  test_file_tag_pattern = input_api.re.compile(
    r'_[a-z]+test(?=(_[a-zA-Z0-9]+)?\.)')
  if_pattern = input_api.re.compile(
      r'\s*#\s*(if|elif|else|endif|define|undef).*')
  # Some files need specialized order of includes; exclude such files from this
  # check.
  uncheckable_includes_pattern = input_api.re.compile(
      r'\s*#include '
      '("ipc/.*macros\.h"|<windows\.h>|".*gl.*autogen.h")\s*')

  contents = f.NewContents()
  warnings = []
  line_num = 0

  # Handle the special first include. If the first include file is
  # some/path/file.h, the corresponding including file can be some/path/file.cc,
  # some/other/path/file.cc, some/path/file_platform.cc, some/path/file-suffix.h
  # etc. It's also possible that no special first include exists.
  # If the included file is some/path/file_platform.h the including file could
  # also be some/path/file_xxxtest_platform.h.
  including_file_base_name = test_file_tag_pattern.sub(
    '', input_api.os_path.basename(f.LocalPath()))

  for line in contents:
    line_num += 1
    if system_include_pattern.match(line):
      # No special first include -> process the line again along with normal
      # includes.
      line_num -= 1
      break
    match = custom_include_pattern.match(line)
    if match:
      match_dict = match.groupdict()
      header_basename = test_file_tag_pattern.sub(
        '', input_api.os_path.basename(match_dict['FILE'])).replace('.h', '')

      if header_basename not in including_file_base_name:
        # No special first include -> process the line again along with normal
        # includes.
        line_num -= 1
      break

  # Split into scopes: Each region between #if and #endif is its own scope.
  scopes = []
  current_scope = []
  for line in contents[line_num:]:
    line_num += 1
    if uncheckable_includes_pattern.match(line):
      continue
    if if_pattern.match(line):
      scopes.append(current_scope)
      current_scope = []
    elif ((system_include_pattern.match(line) or
           custom_include_pattern.match(line)) and
          not excluded_include_pattern.match(line)):
      current_scope.append((line_num, line))
  scopes.append(current_scope)

  for scope in scopes:
    warnings.extend(_CheckIncludeOrderForScope(scope, input_api, f.LocalPath(),
                                               changed_linenums))
  return warnings


def _CheckIncludeOrder(input_api, output_api):
  """Checks that the #include order is correct.

  1. The corresponding header for source files.
  2. C system files in alphabetical order
  3. C++ system files in alphabetical order
  4. Project's .h files in alphabetical order

  Each region separated by #if, #elif, #else, #endif, #define and #undef follows
  these rules separately.
  """
  def FileFilterIncludeOrder(affected_file):
    black_list = (_EXCLUDED_PATHS + input_api.DEFAULT_BLACK_LIST)
    return input_api.FilterSourceFile(affected_file, black_list=black_list)

  warnings = []
  for f in input_api.AffectedFiles(file_filter=FileFilterIncludeOrder):
    if f.LocalPath().endswith(('.cc', '.h')):
      changed_linenums = set(line_num for line_num, _ in f.ChangedContents())
      warnings.extend(_CheckIncludeOrderInFile(input_api, f, changed_linenums))

  results = []
  if warnings:
    results.append(output_api.PresubmitPromptOrNotify(_INCLUDE_ORDER_WARNING,
                                                      warnings))
  return results


def _CheckForVersionControlConflictsInFile(input_api, f):
  pattern = input_api.re.compile('^(?:<<<<<<<|>>>>>>>) |^=======$')
  errors = []
  for line_num, line in f.ChangedContents():
    if pattern.match(line):
      errors.append('    %s:%d %s' % (f.LocalPath(), line_num, line))
  return errors


def _CheckForVersionControlConflicts(input_api, output_api):
  """Usually this is not intentional and will cause a compile failure."""
  errors = []
  for f in input_api.AffectedFiles():
    errors.extend(_CheckForVersionControlConflictsInFile(input_api, f))

  results = []
  if errors:
    results.append(output_api.PresubmitError(
      'Version control conflict markers found, please resolve.', errors))
  return results


def _CheckHardcodedGoogleHostsInLowerLayers(input_api, output_api):
  def FilterFile(affected_file):
    """Filter function for use with input_api.AffectedSourceFiles,
    below.  This filters out everything except non-test files from
    top-level directories that generally speaking should not hard-code
    service URLs (e.g. src/android_webview/, src/content/ and others).
    """
    return input_api.FilterSourceFile(
      affected_file,
      white_list=(r'^(android_webview|base|content|net)[\\\/].*', ),
      black_list=(_EXCLUDED_PATHS +
                  _TEST_CODE_EXCLUDED_PATHS +
                  input_api.DEFAULT_BLACK_LIST))

  base_pattern = '"[^"]*google\.com[^"]*"'
  comment_pattern = input_api.re.compile('//.*%s' % base_pattern)
  pattern = input_api.re.compile(base_pattern)
  problems = []  # items are (filename, line_number, line)
  for f in input_api.AffectedSourceFiles(FilterFile):
    for line_num, line in f.ChangedContents():
      if not comment_pattern.search(line) and pattern.search(line):
        problems.append((f.LocalPath(), line_num, line))

  if problems:
    return [output_api.PresubmitPromptOrNotify(
        'Most layers below src/chrome/ should not hardcode service URLs.\n'
        'Are you sure this is correct?',
        ['  %s:%d:  %s' % (
            problem[0], problem[1], problem[2]) for problem in problems])]
  else:
    return []


def _CheckNoAbbreviationInPngFileName(input_api, output_api):
  """Makes sure there are no abbreviations in the name of PNG files.
  """
  pattern = input_api.re.compile(r'.*_[a-z]_.*\.png$|.*_[a-z]\.png$')
  errors = []
  for f in input_api.AffectedFiles(include_deletes=False):
    if pattern.match(f.LocalPath()):
      errors.append('    %s' % f.LocalPath())

  results = []
  if errors:
    results.append(output_api.PresubmitError(
        'The name of PNG files should not have abbreviations. \n'
        'Use _hover.png, _center.png, instead of _h.png, _c.png.\n'
        'Contact oshima@chromium.org if you have questions.', errors))
  return results


def _FilesToCheckForIncomingDeps(re, changed_lines):
  """Helper method for _CheckAddedDepsHaveTargetApprovals. Returns
  a set of DEPS entries that we should look up.

  For a directory (rather than a specific filename) we fake a path to
  a specific filename by adding /DEPS. This is chosen as a file that
  will seldom or never be subject to per-file include_rules.
  """
  # We ignore deps entries on auto-generated directories.
  AUTO_GENERATED_DIRS = ['grit', 'jni']

  # This pattern grabs the path without basename in the first
  # parentheses, and the basename (if present) in the second. It
  # relies on the simple heuristic that if there is a basename it will
  # be a header file ending in ".h".
  pattern = re.compile(
      r"""['"]\+([^'"]+?)(/[a-zA-Z0-9_]+\.h)?['"].*""")
  results = set()
  for changed_line in changed_lines:
    m = pattern.match(changed_line)
    if m:
      path = m.group(1)
      if path.split('/')[0] not in AUTO_GENERATED_DIRS:
        if m.group(2):
          results.add('%s%s' % (path, m.group(2)))
        else:
          results.add('%s/DEPS' % path)
  return results


def _CheckAddedDepsHaveTargetApprovals(input_api, output_api):
  """When a dependency prefixed with + is added to a DEPS file, we
  want to make sure that the change is reviewed by an OWNER of the
  target file or directory, to avoid layering violations from being
  introduced. This check verifies that this happens.
  """
  changed_lines = set()
  for f in input_api.AffectedFiles():
    filename = input_api.os_path.basename(f.LocalPath())
    if filename == 'DEPS':
      changed_lines |= set(line.strip()
                           for line_num, line
                           in f.ChangedContents())
  if not changed_lines:
    return []

  virtual_depended_on_files = _FilesToCheckForIncomingDeps(input_api.re,
                                                           changed_lines)
  if not virtual_depended_on_files:
    return []

  if input_api.is_committing:
    if input_api.tbr:
      return [output_api.PresubmitNotifyResult(
          '--tbr was specified, skipping OWNERS check for DEPS additions')]
    if not input_api.change.issue:
      return [output_api.PresubmitError(
          "DEPS approval by OWNERS check failed: this change has "
          "no Rietveld issue number, so we can't check it for approvals.")]
    output = output_api.PresubmitError
  else:
    output = output_api.PresubmitNotifyResult

  owners_db = input_api.owners_db
  owner_email, reviewers = input_api.canned_checks._RietveldOwnerAndReviewers(
      input_api,
      owners_db.email_regexp,
      approval_needed=input_api.is_committing)

  owner_email = owner_email or input_api.change.author_email

  reviewers_plus_owner = set(reviewers)
  if owner_email:
    reviewers_plus_owner.add(owner_email)
  missing_files = owners_db.files_not_covered_by(virtual_depended_on_files,
                                                 reviewers_plus_owner)

  # We strip the /DEPS part that was added by
  # _FilesToCheckForIncomingDeps to fake a path to a file in a
  # directory.
  def StripDeps(path):
    start_deps = path.rfind('/DEPS')
    if start_deps != -1:
      return path[:start_deps]
    else:
      return path
  unapproved_dependencies = ["'+%s'," % StripDeps(path)
                             for path in missing_files]

  if unapproved_dependencies:
    output_list = [
      output('Missing LGTM from OWNERS of dependencies added to DEPS:\n    %s' %
             '\n    '.join(sorted(unapproved_dependencies)))]
    if not input_api.is_committing:
      suggested_owners = owners_db.reviewers_for(missing_files, owner_email)
      output_list.append(output(
          'Suggested missing target path OWNERS:\n    %s' %
          '\n    '.join(suggested_owners or [])))
    return output_list

  return []


def _CheckSpamLogging(input_api, output_api):
  file_inclusion_pattern = r'.+%s' % _IMPLEMENTATION_EXTENSIONS
  black_list = (_EXCLUDED_PATHS +
                _TEST_CODE_EXCLUDED_PATHS +
                input_api.DEFAULT_BLACK_LIST +
                (r"^base[\\\/]logging\.h$",
                 r"^base[\\\/]logging\.cc$",
                 r"^chrome[\\\/]app[\\\/]chrome_main_delegate\.cc$",
                 r"^chrome[\\\/]browser[\\\/]chrome_browser_main\.cc$",
                 r"^chrome[\\\/]browser[\\\/]ui[\\\/]startup[\\\/]"
                     r"startup_browser_creator\.cc$",
                 r"^chrome[\\\/]installer[\\\/]setup[\\\/].*",
                 r"chrome[\\\/]browser[\\\/]diagnostics[\\\/]" +
                     r"diagnostics_writer\.cc$",
                 r"^chrome_elf[\\\/]dll_hash[\\\/]dll_hash_main\.cc$",
                 r"^chromecast[\\\/]",
                 r"^cloud_print[\\\/]",
                 r"^content[\\\/]common[\\\/]gpu[\\\/]client[\\\/]"
                     r"gl_helper_benchmark\.cc$",
                 r"^courgette[\\\/]courgette_tool\.cc$",
                 r"^extensions[\\\/]renderer[\\\/]logging_native_handler\.cc$",
                 r"^native_client_sdk[\\\/]",
                 r"^remoting[\\\/]base[\\\/]logging\.h$",
                 r"^remoting[\\\/]host[\\\/].*",
                 r"^sandbox[\\\/]linux[\\\/].*",
                 r"^tools[\\\/]",
                 r"^ui[\\\/]aura[\\\/]bench[\\\/]bench_main\.cc$",
                 r"^webkit[\\\/]browser[\\\/]fileapi[\\\/]" +
                     r"dump_file_system.cc$",))
  source_file_filter = lambda x: input_api.FilterSourceFile(
      x, white_list=(file_inclusion_pattern,), black_list=black_list)

  log_info = []
  printf = []

  for f in input_api.AffectedSourceFiles(source_file_filter):
    contents = input_api.ReadFile(f, 'rb')
    if input_api.re.search(r"\bD?LOG\s*\(\s*INFO\s*\)", contents):
      log_info.append(f.LocalPath())
    elif input_api.re.search(r"\bD?LOG_IF\s*\(\s*INFO\s*,", contents):
      log_info.append(f.LocalPath())

    if input_api.re.search(r"\bprintf\(", contents):
      printf.append(f.LocalPath())
    elif input_api.re.search(r"\bfprintf\((stdout|stderr)", contents):
      printf.append(f.LocalPath())

  if log_info:
    return [output_api.PresubmitError(
      'These files spam the console log with LOG(INFO):',
      items=log_info)]
  if printf:
    return [output_api.PresubmitError(
      'These files spam the console log with printf/fprintf:',
      items=printf)]
  return []


def _CheckForAnonymousVariables(input_api, output_api):
  """These types are all expected to hold locks while in scope and
     so should never be anonymous (which causes them to be immediately
     destroyed)."""
  they_who_must_be_named = [
    'base::AutoLock',
    'base::AutoReset',
    'base::AutoUnlock',
    'SkAutoAlphaRestore',
    'SkAutoBitmapShaderInstall',
    'SkAutoBlitterChoose',
    'SkAutoBounderCommit',
    'SkAutoCallProc',
    'SkAutoCanvasRestore',
    'SkAutoCommentBlock',
    'SkAutoDescriptor',
    'SkAutoDisableDirectionCheck',
    'SkAutoDisableOvalCheck',
    'SkAutoFree',
    'SkAutoGlyphCache',
    'SkAutoHDC',
    'SkAutoLockColors',
    'SkAutoLockPixels',
    'SkAutoMalloc',
    'SkAutoMaskFreeImage',
    'SkAutoMutexAcquire',
    'SkAutoPathBoundsUpdate',
    'SkAutoPDFRelease',
    'SkAutoRasterClipValidate',
    'SkAutoRef',
    'SkAutoTime',
    'SkAutoTrace',
    'SkAutoUnref',
  ]
  anonymous = r'(%s)\s*[({]' % '|'.join(they_who_must_be_named)
  # bad: base::AutoLock(lock.get());
  # not bad: base::AutoLock lock(lock.get());
  bad_pattern = input_api.re.compile(anonymous)
  # good: new base::AutoLock(lock.get())
  good_pattern = input_api.re.compile(r'\bnew\s*' + anonymous)
  errors = []

  for f in input_api.AffectedFiles():
    if not f.LocalPath().endswith(('.cc', '.h', '.inl', '.m', '.mm')):
      continue
    for linenum, line in f.ChangedContents():
      if bad_pattern.search(line) and not good_pattern.search(line):
        errors.append('%s:%d' % (f.LocalPath(), linenum))

  if errors:
    return [output_api.PresubmitError(
      'These lines create anonymous variables that need to be named:',
      items=errors)]
  return []


def _CheckCygwinShell(input_api, output_api):
  source_file_filter = lambda x: input_api.FilterSourceFile(
      x, white_list=(r'.+\.(gyp|gypi)$',))
  cygwin_shell = []

  for f in input_api.AffectedSourceFiles(source_file_filter):
    for linenum, line in f.ChangedContents():
      if 'msvs_cygwin_shell' in line:
        cygwin_shell.append(f.LocalPath())
        break

  if cygwin_shell:
    return [output_api.PresubmitError(
      'These files should not use msvs_cygwin_shell (the default is 0):',
      items=cygwin_shell)]
  return []


def _CheckUserActionUpdate(input_api, output_api):
  """Checks if any new user action has been added."""
  if any('actions.xml' == input_api.os_path.basename(f) for f in
         input_api.LocalPaths()):
    # If actions.xml is already included in the changelist, the PRESUBMIT
    # for actions.xml will do a more complete presubmit check.
    return []

  file_filter = lambda f: f.LocalPath().endswith(('.cc', '.mm'))
  action_re = r'[^a-zA-Z]UserMetricsAction\("([^"]*)'
  current_actions = None
  for f in input_api.AffectedFiles(file_filter=file_filter):
    for line_num, line in f.ChangedContents():
      match = input_api.re.search(action_re, line)
      if match:
        # Loads contents in tools/metrics/actions/actions.xml to memory. It's
        # loaded only once.
        if not current_actions:
          with open('tools/metrics/actions/actions.xml') as actions_f:
            current_actions = actions_f.read()
        # Search for the matched user action name in |current_actions|.
        for action_name in match.groups():
          action = 'name="{0}"'.format(action_name)
          if action not in current_actions:
            return [output_api.PresubmitPromptWarning(
              'File %s line %d: %s is missing in '
              'tools/metrics/actions/actions.xml. Please run '
              'tools/metrics/actions/extract_actions.py to update.'
              % (f.LocalPath(), line_num, action_name))]
  return []


def _GetJSONParseError(input_api, filename, eat_comments=True):
  try:
    contents = input_api.ReadFile(filename)
    if eat_comments:
      json_comment_eater = input_api.os_path.join(
          input_api.PresubmitLocalPath(),
          'tools', 'json_comment_eater', 'json_comment_eater.py')
      process = input_api.subprocess.Popen(
          [input_api.python_executable, json_comment_eater],
          stdin=input_api.subprocess.PIPE,
          stdout=input_api.subprocess.PIPE,
          universal_newlines=True)
      (contents, _) = process.communicate(input=contents)

    input_api.json.loads(contents)
  except ValueError as e:
    return e
  return None


def _GetIDLParseError(input_api, filename):
  try:
    contents = input_api.ReadFile(filename)
    idl_schema = input_api.os_path.join(
        input_api.PresubmitLocalPath(),
        'tools', 'json_schema_compiler', 'idl_schema.py')
    process = input_api.subprocess.Popen(
        [input_api.python_executable, idl_schema],
        stdin=input_api.subprocess.PIPE,
        stdout=input_api.subprocess.PIPE,
        stderr=input_api.subprocess.PIPE,
        universal_newlines=True)
    (_, error) = process.communicate(input=contents)
    return error or None
  except ValueError as e:
    return e


def _CheckParseErrors(input_api, output_api):
  """Check that IDL and JSON files do not contain syntax errors."""
  actions = {
    '.idl': _GetIDLParseError,
    '.json': _GetJSONParseError,
  }
  # These paths contain test data and other known invalid JSON files.
  excluded_patterns = [
    r'test[\\\/]data[\\\/]',
    r'^components[\\\/]policy[\\\/]resources[\\\/]policy_templates\.json$',
  ]
  # Most JSON files are preprocessed and support comments, but these do not.
  json_no_comments_patterns = [
    r'^testing[\\\/]',
  ]
  # Only run IDL checker on files in these directories.
  idl_included_patterns = [
    r'^chrome[\\\/]common[\\\/]extensions[\\\/]api[\\\/]',
    r'^extensions[\\\/]common[\\\/]api[\\\/]',
  ]

  def get_action(affected_file):
    filename = affected_file.LocalPath()
    return actions.get(input_api.os_path.splitext(filename)[1])

  def MatchesFile(patterns, path):
    for pattern in patterns:
      if input_api.re.search(pattern, path):
        return True
    return False

  def FilterFile(affected_file):
    action = get_action(affected_file)
    if not action:
      return False
    path = affected_file.LocalPath()

    if MatchesFile(excluded_patterns, path):
      return False

    if (action == _GetIDLParseError and
        not MatchesFile(idl_included_patterns, path)):
      return False
    return True

  results = []
  for affected_file in input_api.AffectedFiles(
      file_filter=FilterFile, include_deletes=False):
    action = get_action(affected_file)
    kwargs = {}
    if (action == _GetJSONParseError and
        MatchesFile(json_no_comments_patterns, affected_file.LocalPath())):
      kwargs['eat_comments'] = False
    parse_error = action(input_api,
                         affected_file.AbsoluteLocalPath(),
                         **kwargs)
    if parse_error:
      results.append(output_api.PresubmitError('%s could not be parsed: %s' %
          (affected_file.LocalPath(), parse_error)))
  return results


def _CheckJavaStyle(input_api, output_api):
  """Runs checkstyle on changed java files and returns errors if any exist."""
  import sys
  original_sys_path = sys.path
  try:
    sys.path = sys.path + [input_api.os_path.join(
        input_api.PresubmitLocalPath(), 'tools', 'android', 'checkstyle')]
    import checkstyle
  finally:
    # Restore sys.path to what it was before.
    sys.path = original_sys_path

  return checkstyle.RunCheckstyle(
      input_api, output_api, 'tools/android/checkstyle/chromium-style-5.0.xml')


_DEPRECATED_CSS = [
  # Values
  ( "-webkit-box", "flex" ),
  ( "-webkit-inline-box", "inline-flex" ),
  ( "-webkit-flex", "flex" ),
  ( "-webkit-inline-flex", "inline-flex" ),
  ( "-webkit-min-content", "min-content" ),
  ( "-webkit-max-content", "max-content" ),

  # Properties
  ( "-webkit-background-clip", "background-clip" ),
  ( "-webkit-background-origin", "background-origin" ),
  ( "-webkit-background-size", "background-size" ),
  ( "-webkit-box-shadow", "box-shadow" ),

  # Functions
  ( "-webkit-gradient", "gradient" ),
  ( "-webkit-repeating-gradient", "repeating-gradient" ),
  ( "-webkit-linear-gradient", "linear-gradient" ),
  ( "-webkit-repeating-linear-gradient", "repeating-linear-gradient" ),
  ( "-webkit-radial-gradient", "radial-gradient" ),
  ( "-webkit-repeating-radial-gradient", "repeating-radial-gradient" ),
]

def _CheckNoDeprecatedCSS(input_api, output_api):
  """ Make sure that we don't use deprecated CSS
      properties, functions or values. Our external
      documentation is ignored by the hooks as it
      needs to be consumed by WebKit. """
  results = []
  file_inclusion_pattern = (r".+\.css$",)
  black_list = (_EXCLUDED_PATHS +
                _TEST_CODE_EXCLUDED_PATHS +
                input_api.DEFAULT_BLACK_LIST +
                (r"^chrome/common/extensions/docs",
                 r"^chrome/docs",
                 r"^native_client_sdk"))
  file_filter = lambda f: input_api.FilterSourceFile(
      f, white_list=file_inclusion_pattern, black_list=black_list)
  for fpath in input_api.AffectedFiles(file_filter=file_filter):
    for line_num, line in fpath.ChangedContents():
      for (deprecated_value, value) in _DEPRECATED_CSS:
        if deprecated_value in line:
          results.append(output_api.PresubmitError(
              "%s:%d: Use of deprecated CSS %s, use %s instead" %
              (fpath.LocalPath(), line_num, deprecated_value, value)))
  return results


_DEPRECATED_JS = [
  ( "__lookupGetter__", "Object.getOwnPropertyDescriptor" ),
  ( "__defineGetter__", "Object.defineProperty" ),
  ( "__defineSetter__", "Object.defineProperty" ),
]

def _CheckNoDeprecatedJS(input_api, output_api):
  """Make sure that we don't use deprecated JS in Chrome code."""
  results = []
  file_inclusion_pattern = (r".+\.js$",)  # TODO(dbeam): .html?
  black_list = (_EXCLUDED_PATHS + _TEST_CODE_EXCLUDED_PATHS +
                input_api.DEFAULT_BLACK_LIST)
  file_filter = lambda f: input_api.FilterSourceFile(
      f, white_list=file_inclusion_pattern, black_list=black_list)
  for fpath in input_api.AffectedFiles(file_filter=file_filter):
    for lnum, line in fpath.ChangedContents():
      for (deprecated, replacement) in _DEPRECATED_JS:
        if deprecated in line:
          results.append(output_api.PresubmitError(
              "%s:%d: Use of deprecated JS %s, use %s instead" %
              (fpath.LocalPath(), lnum, deprecated, replacement)))
  return results


def _CheckForOverrideAndFinalRules(input_api, output_api):
  """Checks for final and override used as per C++11"""
  problems = []
  for f in input_api.AffectedFiles():
    if (f.LocalPath().endswith(('.cc', '.cpp', '.h', '.mm'))):
      for line_num, line in f.ChangedContents():
        if (input_api.re.search(r'\b(FINAL|OVERRIDE)\b', line)):
          problems.append('    %s:%d' % (f.LocalPath(), line_num))

  if not problems:
    return []
  return [output_api.PresubmitError('Use C++11\'s |final| and |override| '
                                    'rather than FINAL and OVERRIDE.',
                                    problems)]


def _CommonChecks(input_api, output_api):
  """Checks common to both upload and commit."""
  results = []
  results.extend(input_api.canned_checks.PanProjectChecks(
      input_api, output_api,
      excluded_paths=_EXCLUDED_PATHS + _TESTRUNNER_PATHS))
  results.extend(_CheckAuthorizedAuthor(input_api, output_api))
  results.extend(
      _CheckNoProductionCodeUsingTestOnlyFunctions(input_api, output_api))
  results.extend(_CheckNoIOStreamInHeaders(input_api, output_api))
  results.extend(_CheckNoUNIT_TESTInSourceFiles(input_api, output_api))
  results.extend(_CheckNoNewWStrings(input_api, output_api))
  results.extend(_CheckNoDEPSGIT(input_api, output_api))
  results.extend(_CheckNoBannedFunctions(input_api, output_api))
  results.extend(_CheckNoPragmaOnce(input_api, output_api))
  results.extend(_CheckNoTrinaryTrueFalse(input_api, output_api))
  results.extend(_CheckUnwantedDependencies(input_api, output_api))
  results.extend(_CheckFilePermissions(input_api, output_api))
  results.extend(_CheckNoAuraWindowPropertyHInHeaders(input_api, output_api))
  results.extend(_CheckIncludeOrder(input_api, output_api))
  results.extend(_CheckForVersionControlConflicts(input_api, output_api))
  results.extend(_CheckPatchFiles(input_api, output_api))
  results.extend(_CheckHardcodedGoogleHostsInLowerLayers(input_api, output_api))
  results.extend(_CheckNoAbbreviationInPngFileName(input_api, output_api))
  results.extend(_CheckForInvalidOSMacros(input_api, output_api))
  results.extend(_CheckForInvalidIfDefinedMacros(input_api, output_api))
  # TODO(danakj): Remove this when base/move.h is removed.
  results.extend(_CheckForUsingSideEffectsOfPass(input_api, output_api))
  results.extend(_CheckAddedDepsHaveTargetApprovals(input_api, output_api))
  results.extend(
      input_api.canned_checks.CheckChangeHasNoTabs(
          input_api,
          output_api,
          source_file_filter=lambda x: x.LocalPath().endswith('.grd')))
  results.extend(_CheckSpamLogging(input_api, output_api))
  results.extend(_CheckForAnonymousVariables(input_api, output_api))
  results.extend(_CheckCygwinShell(input_api, output_api))
  results.extend(_CheckUserActionUpdate(input_api, output_api))
  results.extend(_CheckNoDeprecatedCSS(input_api, output_api))
  results.extend(_CheckNoDeprecatedJS(input_api, output_api))
  results.extend(_CheckParseErrors(input_api, output_api))
  results.extend(_CheckForIPCRules(input_api, output_api))
  results.extend(_CheckForOverrideAndFinalRules(input_api, output_api))

  if any('PRESUBMIT.py' == f.LocalPath() for f in input_api.AffectedFiles()):
    results.extend(input_api.canned_checks.RunUnitTestsInDirectory(
        input_api, output_api,
        input_api.PresubmitLocalPath(),
        whitelist=[r'^PRESUBMIT_test\.py$']))
  return results


def _CheckAuthorizedAuthor(input_api, output_api):
  """For non-googler/chromites committers, verify the author's email address is
  in AUTHORS.
  """
  # TODO(maruel): Add it to input_api?
  import fnmatch

  author = input_api.change.author_email
  if not author:
    input_api.logging.info('No author, skipping AUTHOR check')
    return []
  authors_path = input_api.os_path.join(
      input_api.PresubmitLocalPath(), 'AUTHORS')
  valid_authors = (
      input_api.re.match(r'[^#]+\s+\<(.+?)\>\s*$', line)
      for line in open(authors_path))
  valid_authors = [item.group(1).lower() for item in valid_authors if item]
  if not any(fnmatch.fnmatch(author.lower(), valid) for valid in valid_authors):
    input_api.logging.info('Valid authors are %s', ', '.join(valid_authors))
    return [output_api.PresubmitPromptWarning(
        ('%s is not in AUTHORS file. If you are a new contributor, please visit'
        '\n'
        'http://www.chromium.org/developers/contributing-code and read the '
        '"Legal" section\n'
        'If you are a chromite, verify the contributor signed the CLA.') %
        author)]
  return []


def _CheckPatchFiles(input_api, output_api):
  problems = [f.LocalPath() for f in input_api.AffectedFiles()
      if f.LocalPath().endswith(('.orig', '.rej'))]
  if problems:
    return [output_api.PresubmitError(
        "Don't commit .rej and .orig files.", problems)]
  else:
    return []


def _DidYouMeanOSMacro(bad_macro):
  try:
    return {'A': 'OS_ANDROID',
            'B': 'OS_BSD',
            'C': 'OS_CHROMEOS',
            'F': 'OS_FREEBSD',
            'L': 'OS_LINUX',
            'M': 'OS_MACOSX',
            'N': 'OS_NACL',
            'O': 'OS_OPENBSD',
            'P': 'OS_POSIX',
            'S': 'OS_SOLARIS',
            'W': 'OS_WIN'}[bad_macro[3].upper()]
  except KeyError:
    return ''


def _CheckForInvalidOSMacrosInFile(input_api, f):
  """Check for sensible looking, totally invalid OS macros."""
  preprocessor_statement = input_api.re.compile(r'^\s*#')
  os_macro = input_api.re.compile(r'defined\((OS_[^)]+)\)')
  results = []
  for lnum, line in f.ChangedContents():
    if preprocessor_statement.search(line):
      for match in os_macro.finditer(line):
        if not match.group(1) in _VALID_OS_MACROS:
          good = _DidYouMeanOSMacro(match.group(1))
          did_you_mean = ' (did you mean %s?)' % good if good else ''
          results.append('    %s:%d %s%s' % (f.LocalPath(),
                                             lnum,
                                             match.group(1),
                                             did_you_mean))
  return results


def _CheckForInvalidOSMacros(input_api, output_api):
  """Check all affected files for invalid OS macros."""
  bad_macros = []
  for f in input_api.AffectedFiles():
    if not f.LocalPath().endswith(('.py', '.js', '.html', '.css')):
      bad_macros.extend(_CheckForInvalidOSMacrosInFile(input_api, f))

  if not bad_macros:
    return []

  return [output_api.PresubmitError(
      'Possibly invalid OS macro[s] found. Please fix your code\n'
      'or add your macro to src/PRESUBMIT.py.', bad_macros)]


def _CheckForInvalidIfDefinedMacrosInFile(input_api, f):
  """Check all affected files for invalid "if defined" macros."""
  ALWAYS_DEFINED_MACROS = (
      "TARGET_CPU_PPC",
      "TARGET_CPU_PPC64",
      "TARGET_CPU_68K",
      "TARGET_CPU_X86",
      "TARGET_CPU_ARM",
      "TARGET_CPU_MIPS",
      "TARGET_CPU_SPARC",
      "TARGET_CPU_ALPHA",
      "TARGET_IPHONE_SIMULATOR",
      "TARGET_OS_EMBEDDED",
      "TARGET_OS_IPHONE",
      "TARGET_OS_MAC",
      "TARGET_OS_UNIX",
      "TARGET_OS_WIN32",
  )
  ifdef_macro = input_api.re.compile(r'^\s*#.*(?:ifdef\s|defined\()([^\s\)]+)')
  results = []
  for lnum, line in f.ChangedContents():
    for match in ifdef_macro.finditer(line):
      if match.group(1) in ALWAYS_DEFINED_MACROS:
        always_defined = ' %s is always defined. ' % match.group(1)
        did_you_mean = 'Did you mean \'#if %s\'?' % match.group(1)
        results.append('    %s:%d %s\n\t%s' % (f.LocalPath(),
                                               lnum,
                                               always_defined,
                                               did_you_mean))
  return results


def _CheckForInvalidIfDefinedMacros(input_api, output_api):
  """Check all affected files for invalid "if defined" macros."""
  bad_macros = []
  for f in input_api.AffectedFiles():
    if f.LocalPath().endswith(('.h', '.c', '.cc', '.m', '.mm')):
      bad_macros.extend(_CheckForInvalidIfDefinedMacrosInFile(input_api, f))

  if not bad_macros:
    return []

  return [output_api.PresubmitError(
      'Found ifdef check on always-defined macro[s]. Please fix your code\n'
      'or check the list of ALWAYS_DEFINED_MACROS in src/PRESUBMIT.py.',
      bad_macros)]


def _CheckForUsingSideEffectsOfPass(input_api, output_api):
  """Check all affected files for using side effects of Pass."""
  errors = []
  for f in input_api.AffectedFiles():
    if f.LocalPath().endswith(('.h', '.c', '.cc', '.m', '.mm')):
      for lnum, line in f.ChangedContents():
        # Disallow Foo(*my_scoped_thing.Pass()); See crbug.com/418297.
        if input_api.re.search(r'\*[a-zA-Z0-9_]+\.Pass\(\)', line):
          errors.append(output_api.PresubmitError(
            ('%s:%d uses *foo.Pass() to delete the contents of scoped_ptr. ' +
             'See crbug.com/418297.') % (f.LocalPath(), lnum)))
  return errors


def _CheckForIPCRules(input_api, output_api):
  """Check for same IPC rules described in
  http://www.chromium.org/Home/chromium-security/education/security-tips-for-ipc
  """
  base_pattern = r'IPC_ENUM_TRAITS\('
  inclusion_pattern = input_api.re.compile(r'(%s)' % base_pattern)
  comment_pattern = input_api.re.compile(r'//.*(%s)' % base_pattern)

  problems = []
  for f in input_api.AffectedSourceFiles(None):
    local_path = f.LocalPath()
    if not local_path.endswith('.h'):
      continue
    for line_number, line in f.ChangedContents():
      if inclusion_pattern.search(line) and not comment_pattern.search(line):
        problems.append(
          '%s:%d\n    %s' % (local_path, line_number, line.strip()))

  if problems:
    return [output_api.PresubmitPromptWarning(
        _IPC_ENUM_TRAITS_DEPRECATED, problems)]
  else:
    return []


def CheckChangeOnUpload(input_api, output_api):
  results = []
  results.extend(_CommonChecks(input_api, output_api))
  results.extend(_CheckValidHostsInDEPS(input_api, output_api))
  results.extend(_CheckJavaStyle(input_api, output_api))
  return results


def GetTryServerMasterForBot(bot):
  """Returns the Try Server master for the given bot.

  It tries to guess the master from the bot name, but may still fail
  and return None.  There is no longer a default master.
  """
  # Potentially ambiguous bot names are listed explicitly.
  master_map = {
      'linux_gpu': 'tryserver.chromium.gpu',
      'mac_gpu': 'tryserver.chromium.gpu',
      'win_gpu': 'tryserver.chromium.gpu',
      'chromium_presubmit': 'tryserver.chromium.linux',
      'blink_presubmit': 'tryserver.chromium.linux',
      'tools_build_presubmit': 'tryserver.chromium.linux',
  }
  master = master_map.get(bot)
  if not master:
    if 'gpu' in bot:
      master = 'tryserver.chromium.gpu'
    elif 'linux' in bot or 'android' in bot or 'presubmit' in bot:
      master = 'tryserver.chromium.linux'
    elif 'win' in bot:
      master = 'tryserver.chromium.win'
    elif 'mac' in bot or 'ios' in bot:
      master = 'tryserver.chromium.mac'
  return master


def GetDefaultTryConfigs(bots=None):
  """Returns a list of ('bot', set(['tests']), optionally filtered by [bots].

  To add tests to this list, they MUST be in the the corresponding master's
  gatekeeper config. For example, anything on master.chromium would be closed by
  tools/build/masters/master.chromium/master_gatekeeper_cfg.py.

  If 'bots' is specified, will only return configurations for bots in that list.
  """

  standard_tests = [
      'base_unittests',
      'browser_tests',
      'cacheinvalidation_unittests',
      'check_deps',
      'check_deps2git',
      'content_browsertests',
      'content_unittests',
      'crypto_unittests',
      'gpu_unittests',
      'interactive_ui_tests',
      'ipc_tests',
      'jingle_unittests',
      'media_unittests',
      'net_unittests',
      'ppapi_unittests',
      'printing_unittests',
      'sql_unittests',
      'sync_unit_tests',
      'unit_tests',
      # Broken in release.
      #'url_unittests',
      #'webkit_unit_tests',
  ]

  builders_and_tests = {
      # TODO(maruel): Figure out a way to run 'sizes' where people can
      # effectively update the perf expectation correctly.  This requires a
      # clobber=True build running 'sizes'. 'sizes' is not accurate with
      # incremental build. Reference:
      # http://chromium.org/developers/tree-sheriffs/perf-sheriffs.
      # TODO(maruel): An option would be to run 'sizes' but not count a failure
      # of this step as a try job failure.
      'android_aosp': ['compile'],
      'android_arm64_dbg_recipe': ['slave_steps'],
      'android_chromium_gn_compile_dbg': ['compile'],
      'android_chromium_gn_compile_rel': ['compile'],
      'android_clang_dbg': ['slave_steps'],
      'android_clang_dbg_recipe': ['slave_steps'],
      'android_dbg_tests_recipe': ['slave_steps'],
      'cros_x86': ['defaulttests'],
      'ios_dbg_simulator': [
          'compile',
          'base_unittests',
          'content_unittests',
          'crypto_unittests',
          'url_unittests',
          'net_unittests',
          'sql_unittests',
          'ui_base_unittests',
          'ui_unittests',
      ],
      'ios_rel_device': ['compile'],
      'ios_rel_device_ninja': ['compile'],
      'mac_asan': ['compile'],
      #TODO(stip): Change the name of this builder to reflect that it's release.
      'linux_gtk': standard_tests,
      'linux_chromeos_asan': ['compile'],
      'linux_chromium_chromeos_clang_dbg': ['defaulttests'],
      'linux_chromium_chromeos_rel_swarming': ['defaulttests'],
      'linux_chromium_compile_dbg': ['defaulttests'],
      'linux_chromium_gn_dbg': ['compile'],
      'linux_chromium_gn_rel': ['defaulttests'],
      'linux_chromium_rel_swarming': ['defaulttests'],
      'linux_chromium_clang_dbg': ['defaulttests'],
      'linux_gpu': ['defaulttests'],
      'linux_nacl_sdk_build': ['compile'],
      'mac_chromium_compile_dbg': ['defaulttests'],
      'mac_chromium_rel_swarming': ['defaulttests'],
      'mac_gpu': ['defaulttests'],
      'mac_nacl_sdk_build': ['compile'],
      'win_chromium_compile_dbg': ['defaulttests'],
      'win_chromium_dbg': ['defaulttests'],
      'win_chromium_rel_swarming': ['defaulttests'],
      'win_chromium_x64_rel_swarming': ['defaulttests'],
      'win_gpu': ['defaulttests'],
      'win_nacl_sdk_build': ['compile'],
      'win8_chromium_rel': ['defaulttests'],
  }

  if bots:
    filtered_builders_and_tests = dict((bot, set(builders_and_tests[bot]))
                                       for bot in bots)
  else:
    filtered_builders_and_tests = dict(
        (bot, set(tests))
        for bot, tests in builders_and_tests.iteritems())

  # Build up the mapping from tryserver master to bot/test.
  out = dict()
  for bot, tests in filtered_builders_and_tests.iteritems():
    out.setdefault(GetTryServerMasterForBot(bot), {})[bot] = tests
  return out


def CheckChangeOnCommit(input_api, output_api):
  results = []
  results.extend(_CommonChecks(input_api, output_api))
  # TODO(thestig) temporarily disabled, doesn't work in third_party/
  #results.extend(input_api.canned_checks.CheckSvnModifiedDirectories(
  #    input_api, output_api, sources))
  # Make sure the tree is 'open'.
  results.extend(input_api.canned_checks.CheckTreeIsOpen(
      input_api,
      output_api,
      json_url='http://chromium-status.appspot.com/current?format=json'))

  results.extend(input_api.canned_checks.CheckChangeHasBugField(
      input_api, output_api))
  results.extend(input_api.canned_checks.CheckChangeHasDescription(
      input_api, output_api))
  return results


def GetPreferredTryMasters(project, change):
  import re
  files = change.LocalPaths()

  if not files or all(re.search(r'[\\\/]OWNERS$', f) for f in files):
    return {}

  if all(re.search(r'\.(m|mm)$|(^|[\\\/_])mac[\\\/_.]', f) for f in files):
    return GetDefaultTryConfigs([
        'mac_chromium_compile_dbg',
        'mac_chromium_rel_swarming',
    ])
  if all(re.search('(^|[/_])win[/_.]', f) for f in files):
    return GetDefaultTryConfigs([
        'win_chromium_dbg',
        'win_chromium_rel_swarming',
        'win8_chromium_rel',
    ])
  if all(re.search(r'(^|[\\\/_])android[\\\/_.]', f) for f in files):
    return GetDefaultTryConfigs([
        'android_aosp',
        'android_clang_dbg',
        'android_dbg_tests_recipe',
    ])
  if all(re.search(r'[\\\/_]ios[\\\/_.]', f) for f in files):
    return GetDefaultTryConfigs(['ios_rel_device', 'ios_dbg_simulator'])

  builders = [
      'android_arm64_dbg_recipe',
      'android_chromium_gn_compile_rel',
      'android_chromium_gn_compile_dbg',
      'android_clang_dbg',
      'android_clang_dbg_recipe',
      'android_dbg_tests_recipe',
      'ios_dbg_simulator',
      'ios_rel_device',
      'ios_rel_device_ninja',
      'linux_chromium_chromeos_rel_swarming',
      'linux_chromium_clang_dbg',
      'linux_chromium_gn_dbg',
      'linux_chromium_gn_rel',
      'linux_chromium_rel_swarming',
      'linux_gpu',
      'mac_chromium_compile_dbg',
      'mac_chromium_rel_swarming',
      'mac_gpu',
      'win_chromium_compile_dbg',
      'win_chromium_rel_swarming',
      'win_chromium_x64_rel_swarming',
      'win_gpu',
      'win8_chromium_rel',
  ]

  # Match things like path/aura/file.cc and path/file_aura.cc.
  # Same for chromeos.
  if any(re.search(r'[\\\/_](aura|chromeos)', f) for f in files):
    builders.extend([
        'linux_chromeos_asan',
        'linux_chromium_chromeos_clang_dbg'
    ])

  # If there are gyp changes to base, build, or chromeos, run a full cros build
  # in addition to the shorter linux_chromeos build. Changes to high level gyp
  # files have a much higher chance of breaking the cros build, which is
  # differnt from the linux_chromeos build that most chrome developers test
  # with.
  if any(re.search('^(base|build|chromeos).*\.gypi?$', f) for f in files):
    builders.extend(['cros_x86'])

  # The AOSP bot doesn't build the chrome/ layer, so ignore any changes to it
  # unless they're .gyp(i) files as changes to those files can break the gyp
  # step on that bot.
  if (not all(re.search('^chrome', f) for f in files) or
      any(re.search('\.gypi?$', f) for f in files)):
    builders.extend(['android_aosp'])

  return GetDefaultTryConfigs(builders)
