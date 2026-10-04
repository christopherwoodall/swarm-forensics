[Skip to content](https://github.com/anthropics/claudes-c-compiler#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/anthropics/claudes-c-compiler) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/anthropics/claudes-c-compiler) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/anthropics/claudes-c-compiler) to refresh your session.Dismiss alert

{{ message }}

[anthropics](https://github.com/anthropics)/ **[claudes-c-compiler](https://github.com/anthropics/claudes-c-compiler)** Public

- [Notifications](https://github.com/login?return_to=%2Fanthropics%2Fclaudes-c-compiler) You must be signed in to change notification settings
- [Fork\\
252](https://github.com/login?return_to=%2Fanthropics%2Fclaudes-c-compiler)
- [Star\\
2.8k](https://github.com/login?return_to=%2Fanthropics%2Fclaudes-c-compiler)


main

[**1** Branch](https://github.com/anthropics/claudes-c-compiler/branches) [**0** Tags](https://github.com/anthropics/claudes-c-compiler/tags)

[Go to Branches page](https://github.com/anthropics/claudes-c-compiler/branches)[Go to Tags page](https://github.com/anthropics/claudes-c-compiler/tags)

Go to file

Code

Open more actions menu

## Latest commit

[![carlini](https://avatars.githubusercontent.com/u/1269300?v=4&size=40)](https://github.com/carlini)[carlini](https://github.com/anthropics/claudes-c-compiler/commits?author=carlini)

[Add steps to reproduce kernel defconfig build](https://github.com/anthropics/claudes-c-compiler/commit/6f1b99acb2f4ec2414592136c2009fe7713deec3)

8 months agoFeb 5, 2026

[6f1b99a](https://github.com/anthropics/claudes-c-compiler/commit/6f1b99acb2f4ec2414592136c2009fe7713deec3) · 8 months agoFeb 5, 2026

## History

[3,982 Commits](https://github.com/anthropics/claudes-c-compiler/commits/main/)

Open commit details

[View commit history for this file.](https://github.com/anthropics/claudes-c-compiler/commits/main/) 3,982 Commits

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| [current\_tasks](https://github.com/anthropics/claudes-c-compiler/tree/main/current_tasks "current_tasks") | [current\_tasks](https://github.com/anthropics/claudes-c-compiler/tree/main/current_tasks "current_tasks") | [Remove crate-wide and per-item clippy silences](https://github.com/anthropics/claudes-c-compiler/commit/d3730ef04a5a6afd7b833e4b5b6aa71f7c2f6a31 "Remove crate-wide and per-item clippy silences  Strip the three global #![allow(clippy::...)] directives from lib.rs (too_many_arguments, type_complexity, needless_range_loop) and remove per-item #[allow(clippy::too_many_arguments)] and enum_variant_names suppressions throughout the codebase. Keep only unusual_byte_groupings (RISC-V instruction encoding) and upper_case_acronyms (x86 mnemonics) where the naming is dictated by hardware conventions.  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 8 months agoFeb 5, 2026 |
| [ideas](https://github.com/anthropics/claudes-c-compiler/tree/main/ideas "ideas") | [ideas](https://github.com/anthropics/claudes-c-compiler/tree/main/ideas "ideas") | [Lock task: add ARM assembler CASP/CASPAL instruction support](https://github.com/anthropics/claudes-c-compiler/commit/e0a7ceb5526b47946df1d5d971f56f1785daaaa0 "Lock task: add ARM assembler CASP/CASPAL instruction support") | 8 months agoFeb 5, 2026 |
| [include](https://github.com/anthropics/claudes-c-compiler/tree/main/include "include") | [include](https://github.com/anthropics/claudes-c-compiler/tree/main/include "include") | [Remove task lock: xmmintrin.h emmintrin.h include fix completed](https://github.com/anthropics/claudes-c-compiler/commit/553faeac5d26bdaca6cf2f3d65a48040a446456b "Remove task lock: xmmintrin.h emmintrin.h include fix completed  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 8 months agoFeb 5, 2026 |
| [projects](https://github.com/anthropics/claudes-c-compiler/tree/main/projects "projects") | [projects](https://github.com/anthropics/claudes-c-compiler/tree/main/projects "projects") | [Backend codegen cleanup: eliminate format! allocations, fix data emis…](https://github.com/anthropics/claudes-c-compiler/commit/48d8a13d29365e13768b370fd9710ae464b5ef21 "Backend codegen cleanup: eliminate format! allocations, fix data emission bugs  - variadic.rs: Replace emit(&format!(...)) with emit_fmt(format_args!(...))  to avoid 3 unnecessary heap allocations per va_arg struct emission - riscv/alu.rs: Replace format!(\"add{}\", w) mnemonic construction with  static &str lookup table, eliminating 13 format! allocations per binop - common.rs: Extract emit_u64_as_long_pair() helper for the repeated  pattern of splitting 64-bit values into two .long directives on i686,  reducing 4 duplicate code sites to single-line calls - common.rs: Fix nested Compound global initializer emission to recurse  into elements instead of silently emitting a pointer-sized zero (bug fix:  nested compounds would lose all data and emit incorrect assembly) - common.rs: Fix stale doc comment on emit_block_label - Clean up 5 stale completed task locks - Update cleanup_code_quality.txt backlog with progress  Tests: 99.8% x86, 99.5% ARM, 99.9% RISC-V, 99.9% i686; all 48 projects pass.  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 9 months agoJan 30, 2026 |
| [src](https://github.com/anthropics/claudes-c-compiler/tree/main/src "src") | [src](https://github.com/anthropics/claudes-c-compiler/tree/main/src "src") | [Remove crate-wide and per-item clippy silences](https://github.com/anthropics/claudes-c-compiler/commit/d3730ef04a5a6afd7b833e4b5b6aa71f7c2f6a31 "Remove crate-wide and per-item clippy silences  Strip the three global #![allow(clippy::...)] directives from lib.rs (too_many_arguments, type_complexity, needless_range_loop) and remove per-item #[allow(clippy::too_many_arguments)] and enum_variant_names suppressions throughout the codebase. Keep only unusual_byte_groupings (RISC-V instruction encoding) and upper_case_acronyms (x86 mnemonics) where the naming is dictated by hardware conventions.  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 8 months agoFeb 5, 2026 |
| [.gitignore](https://github.com/anthropics/claudes-c-compiler/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/anthropics/claudes-c-compiler/blob/main/.gitignore ".gitignore") | [Lock: fix\_arm\_kernel\_stack\_overflow\_blake2s (in\_progress)](https://github.com/anthropics/claudes-c-compiler/commit/10b187812baa902f502813c8a9e6dd023ad86c45 "Lock: fix_arm_kernel_stack_overflow_blake2s (in_progress)  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 9 months agoJan 29, 2026 |
| [BUILDING\_LINUX.txt](https://github.com/anthropics/claudes-c-compiler/blob/main/BUILDING_LINUX.txt "BUILDING_LINUX.txt") | [BUILDING\_LINUX.txt](https://github.com/anthropics/claudes-c-compiler/blob/main/BUILDING_LINUX.txt "BUILDING_LINUX.txt") | [Add steps to reproduce kernel defconfig build](https://github.com/anthropics/claudes-c-compiler/commit/6f1b99acb2f4ec2414592136c2009fe7713deec3 "Add steps to reproduce kernel defconfig build") | 8 months agoFeb 5, 2026 |
| [Cargo.toml](https://github.com/anthropics/claudes-c-compiler/blob/main/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/anthropics/claudes-c-compiler/blob/main/Cargo.toml "Cargo.toml") | [Improve docs: add Quick Start, Testing section, fix naming to Claude'…](https://github.com/anthropics/claudes-c-compiler/commit/467b2eb127cce504325a271f1c1d217d3a7deea0 "Improve docs: add Quick Start, Testing section, fix naming to Claude's C Compiler  - Add \"Claude's C Compiler\" as the full project name in README header,  DESIGN_DOC intro, and Cargo.toml description - Add Quick Start section (top-level, before Usage) with hello-world,  cross-compilation, and build system integration examples - Add Testing section explaining unit tests and integration test format - Improve Prerequisites with cross-compilation sysroot requirements - Promote Quick Start to top-level ## section before detailed Usage reference - Use em-dash consistently throughout  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 9 months agoFeb 4, 2026 |
| [DESIGN\_DOC.md](https://github.com/anthropics/claudes-c-compiler/blob/main/DESIGN_DOC.md "DESIGN_DOC.md") | [DESIGN\_DOC.md](https://github.com/anthropics/claudes-c-compiler/blob/main/DESIGN_DOC.md "DESIGN_DOC.md") | [Fix DESIGN\_DOC.md source tree: three .rs files are actually directories](https://github.com/anthropics/claudes-c-compiler/commit/04d5b60758dbf1ccf1a3207e59723953d78158ea "Fix DESIGN_DOC.md source tree: three .rs files are actually directories  stack_layout.rs, elf.rs, and linker_common.rs have been refactored into multi-file module directories. Update the source tree listing to reflect the current structure.  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>") | 8 months agoFeb 5, 2026 |
| [LICENSE](https://github.com/anthropics/claudes-c-compiler/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/anthropics/claudes-c-compiler/blob/main/LICENSE "LICENSE") | [Add disclaimer and LICENSE](https://github.com/anthropics/claudes-c-compiler/commit/e6f3fad053d1ad5f3c9370dbc4221668d858ce6f "Add disclaimer and LICENSE") | 8 months agoFeb 5, 2026 |
| [README.md](https://github.com/anthropics/claudes-c-compiler/blob/main/README.md "README.md") | [README.md](https://github.com/anthropics/claudes-c-compiler/blob/main/README.md "README.md") | [Add disclaimer and LICENSE](https://github.com/anthropics/claudes-c-compiler/commit/e6f3fad053d1ad5f3c9370dbc4221668d858ce6f "Add disclaimer and LICENSE") | 8 months agoFeb 5, 2026 |
| View all files |

## Repository files navigation

# CCC — Claude's C Compiler

[Permalink: CCC — Claude's C Compiler](https://github.com/anthropics/claudes-c-compiler#ccc--claudes-c-compiler)

A C compiler written entirely from scratch in Rust, targeting x86-64, i686,
AArch64, and RISC-V 64. Zero compiler-specific dependencies — the frontend,
SSA-based IR, optimizer, code generator, peephole optimizers, assembler,
linker, and DWARF debug info generation are all implemented from scratch.
Claude's C Compiler produces ELF executables without any external toolchain.

> Note: With the exception of this one paragraph that was written by a human, 100% of the code and documentation in this repository was written by Claude Opus 4.6. A human guided some of this process by writing test cases that Claude was told to pass, but never interactively pair-programmed with Claude to debug or to provide feedback on code quality. As a result, I do not recommend you use this code! None of it has been validated for correctness. Claude wrote this exclusively on a Linux host; it probably will not work on MacOS/Windows — neither I nor Claude have tried. The docs may be wrong and make claims that are false. See [our blog post](https://anthropic.com/engineering/building-c-compiler) for more detail.

## Prerequisites

[Permalink: Prerequisites](https://github.com/anthropics/claudes-c-compiler#prerequisites)

- **Rust** (stable, 2021 edition) — install via [rustup](https://rustup.rs/)
- **Linux host** — the compiler targets Linux ELF executables and relies on
Linux system headers / C runtime libraries (glibc or musl) being installed
on the host
- For cross-compilation targets (ARM, RISC-V, i686), the corresponding
cross-compilation sysroots should be installed (e.g.,
`aarch64-linux-gnu-gcc`, `riscv64-linux-gnu-gcc`)

## Building

[Permalink: Building](https://github.com/anthropics/claudes-c-compiler#building)

```
cargo build --release
```

This produces five binaries in `target/release/`, all compiled from the same
source. The target architecture is selected by the binary name at runtime:

| Binary | Target |
| --- | --- |
| `ccc` | x86-64 (default) |
| `ccc-x86` | x86-64 |
| `ccc-arm` | AArch64 |
| `ccc-riscv` | RISC-V 64 |
| `ccc-i686` | i686 (32-bit x86) |

## Quick Start

[Permalink: Quick Start](https://github.com/anthropics/claudes-c-compiler#quick-start)

Compile and run a simple C program:

```
# Write a test program
cat > hello.c << 'EOF'
#include <stdio.h>
int main(void) {
    printf("Hello from CCC!\n");
    return 0;
}
EOF

# Compile and run (x86-64)
./target/release/ccc -o hello hello.c
./hello

# Cross-compile for AArch64 and run under QEMU
./target/release/ccc-arm -o hello-arm hello.c
qemu-aarch64 -L /usr/aarch64-linux-gnu ./hello-arm
```

CCC works as a drop-in GCC replacement. Point your build system at it:

```
# Build a project with make
make CC=/path/to/ccc-x86

# Build a project with CMake
cmake -DCMAKE_C_COMPILER=/path/to/ccc-x86 ..

# Build a project with configure scripts
./configure CC=/path/to/ccc-x86
```

## Usage

[Permalink: Usage](https://github.com/anthropics/claudes-c-compiler#usage)

```
# Compile and link
ccc -o output input.c                # x86-64
ccc-arm -o output input.c            # AArch64
ccc-riscv -o output input.c          # RISC-V 64
ccc-i686 -o output input.c           # i686

# GCC-compatible flags
ccc -S input.c                       # Emit assembly
ccc -c input.c                       # Compile to object file
ccc -E input.c                       # Preprocess only
ccc -O2 -o output input.c            # Optimize (accepts -O0 through -O3, -Os, -Oz)
ccc -g -o output input.c             # DWARF debug info
ccc -DFOO=1 -Iinclude/ input.c       # Define macros, add include paths
ccc -Werror -Wall input.c            # Warning control
ccc -fPIC -shared -o lib.so lib.c    # Position-independent code
ccc -x c -E -                        # Read from stdin

# Build system integration (reports as GCC 14.2.0 for compatibility)
ccc -dumpmachine     # x86_64-linux-gnu / aarch64-linux-gnu / riscv64-linux-gnu / i686-linux-gnu
ccc -dumpversion     # 14
```

The compiler accepts most GCC flags. Unrecognized flags (e.g., architecture-
specific `-m` flags, unknown `-f` flags) are silently ignored so `ccc` can
serve as a drop-in GCC replacement in build systems.

### Assembler and Linker Modes

[Permalink: Assembler and Linker Modes](https://github.com/anthropics/claudes-c-compiler#assembler-and-linker-modes)

By default, the compiler uses its **builtin assembler and linker** for all
four architectures. No external toolchain is required. You can verify this
with `--version`, which shows `Backend: standalone` when using the builtin
tools.

To build with optional GCC fallback support (e.g., for debugging), enable
Cargo features at compile time:

```
# Build with GCC assembler and linker fallback
cargo build --release --features gcc_assembler,gcc_linker

# Build with GCC fallback for -m16 boot code only
cargo build --release --features gcc_m16
```

| Feature | Description |
| --- | --- |
| `gcc_assembler` | Use GCC as the assembler instead of the builtin |
| `gcc_linker` | Use GCC as the linker instead of the builtin |
| `gcc_m16` | Use GCC for `-m16` (16-bit real mode boot code) |

When compiled with GCC fallback features enabled, `--version` shows which
components use GCC (e.g., `Backend: gcc_assembler, gcc_linker`).

## Status

[Permalink: Status](https://github.com/anthropics/claudes-c-compiler#status)

The compiler can build real-world C codebases across all four architectures,
including the Linux kernel. Projects that compile and pass their test suites
include PostgreSQL (all 237 regression tests), SQLite, QuickJS, zlib, Lua,
libsodium, libpng, jq, libjpeg-turbo, mbedTLS, libuv, Redis, libffi, musl,
TCC, and DOOM — all using the fully standalone assembler and linker with no
external toolchain. Over 150 additional projects have also been built
successfully, including FFmpeg (all 7331 FATE checkasm tests on x86-64 and
AArch64), GNU coreutils, Busybox, CPython, QEMU, and LuaJIT.

### Known Limitations

[Permalink: Known Limitations](https://github.com/anthropics/claudes-c-compiler#known-limitations)

- **Optimization levels**: All levels (`-O0` through `-O3`, `-Os`, `-Oz`) run
the same optimization pipeline. Separate tiers will be added as the compiler
matures.
- **Long double**: x86 80-bit extended precision is supported via x87 FPU
instructions. On ARM/RISC-V, `long double` is IEEE binary128 via
compiler-rt/libgcc soft-float libcalls.
- **Complex numbers**: `_Complex` arithmetic has some edge-case failures.
- **GNU extensions**: Partial `__attribute__` support. NEON intrinsics are
partially implemented (core 128-bit operations work).
- **Atomics**: `_Atomic` is parsed but treated as the underlying type (the
qualifier is not tracked through the type system).

## Testing

[Permalink: Testing](https://github.com/anthropics/claudes-c-compiler#testing)

The compiler has two kinds of tests:

**Unit tests** (in-source `#[test]` functions for individual passes and modules):

```
cargo test --release
```

**Integration tests** (end-to-end compilation tests in `tests/`). Each test is
a directory containing a `main.c` source file and expected output files:

```
tests/
  some-test-name/
    main.c              # C source to compile
    expected.stdout     # Expected stdout (if any)
    expected.ret        # Expected exit code (if any)
    expected.skip.arm   # Skip marker for specific architectures (optional)
```

Tests are run by compiling `main.c` with `ccc`, executing the resulting binary,
and comparing stdout and the exit code against the expected files.

## Environment Variables

[Permalink: Environment Variables](https://github.com/anthropics/claudes-c-compiler#environment-variables)

| Variable | Purpose |
| --- | --- |
| `CCC_TIME_PHASES` | Print per-phase compilation timing to stderr |
| `CCC_TIME_PASSES` | Print per-pass optimization timing and change counts to stderr |
| `CCC_DISABLE_PASSES` | Disable specific optimization passes (comma-separated, or `all`) |
| `CCC_KEEP_ASM` | Preserve intermediate `.s` files next to output |
| `CCC_ASM_DEBUG` | Dump preprocessed assembly to `/tmp/asm_debug_<name>.s` |

## Project Organization

[Permalink: Project Organization](https://github.com/anthropics/claudes-c-compiler#project-organization)

```
src/                Compiler source code (Rust)
  frontend/         C source -> typed AST (preprocessor, lexer, parser, sema)
  ir/               Target-independent SSA IR (lowering, mem2reg)
  passes/           SSA optimization passes (15 passes + shared loop analysis)
  backend/          IR -> assembly -> machine code -> ELF (4 architectures)
  common/           Shared types, symbol table, diagnostics
  driver/           CLI parsing, pipeline orchestration

include/            Bundled C headers (x86 SIMD: SSE through AVX-512, AES-NI, FMA, SHA, BMI2; ARM NEON)
tests/              Compiler tests (each test is a directory with main.c and expected output)
ideas/              Future work proposals and improvement notes
```

Each `src/` subdirectory has its own `README.md` with detailed design
documentation. For the full architecture, compilation pipeline data flow,
and key design decisions, see [DESIGN\_DOC.md](https://github.com/anthropics/claudes-c-compiler/blob/main/DESIGN_DOC.md).

## About

Claude Opus 4.6 wrote a dependency-free C compiler in Rust, with backends targeting x86 (64- and 32-bit), ARM, and RISC-V, capable of compiling a booting Linux kernel.

### Resources

[Readme](https://github.com/anthropics/claudes-c-compiler#readme-ov-file)

[CC0-1.0 license](https://github.com/anthropics/claudes-c-compiler#CC0-1.0-1-ov-file)

[Activity](https://github.com/anthropics/claudes-c-compiler/activity)

[Custom properties](https://github.com/anthropics/claudes-c-compiler/custom-properties)

### Stars

**2.8k** stars

### Watchers

**35** watching

### Forks

[**252** forks](https://github.com/anthropics/claudes-c-compiler/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fanthropics%2Fclaudes-c-compiler&report=anthropics+%28user%29)

## Releases

## Packages

## Used by

## Contributors

## Languages

You can’t perform that action at this time.