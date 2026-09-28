<div align="center">

# Hi, I'm Alexandra! 👋

*Computer Science student at Politehnica University of Bucharest, mostly interested in low-level programming, systems and security.*

[![Portfolio](https://img.shields.io/badge/PORTFOLIO-F3A6C6?style=for-the-badge&logo=github&logoColor=black)](https://lupsalexandra33.github.io)
[![Email](https://img.shields.io/badge/EMAIL-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:alexandralupsa5@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LINKEDIN-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/lupsalexandra33/)

</div>

### Open source

**[Unikraft](https://github.com/unikraft)** - open-source unikernel SDK

*Catalog manifests* - standardising how applications declare their Kraftfile build specifications and dependencies.

- [catalog #255](https://github.com/unikraft/catalog/pull/255) - **merged**
- [catalog #256](https://github.com/unikraft/catalog/pull/256) - **merged**
- [catalog #244](https://github.com/unikraft/catalog/pull/244) - *in review*

*Ruby support* - porting the interpreter and adding a Ruby application to the catalog.

- [catalog-core #91](https://github.com/unikraft/catalog-core/pull/91) - *in review* - `ruby-hello`, a catalog
  application with Firecracker support (475 LOC, 13 files). Closes
  [#25](https://github.com/unikraft/catalog-core/issues/25).
- [lib-ruby #4](https://github.com/unikraft/lib-ruby/pull/4) - *in review* - retargets the port to Ruby 4.0.6
  on musl, as agreed with the maintainers.
- Root-caused a build failure open since 2021
  ([lib-ruby #1](https://github.com/unikraft/lib-ruby/issues/1)): the archive `lib-ruby` fetches ships
  `configure.ac` but neither the generated `configure` nor `tool/config.guess` / `tool/config.sub`, so
  `autoconf` regenerates the script and the build aborts on the missing auxiliary files. Proposed fetching the
  official release tarball from `cache.ruby-lang.org` instead, which ships all three.
- Also surfaced an OpenSSL 3.0 incompatibility in Ruby 2.6 and two gaps in the Unikraft core
  (`sys/prctl.h`, `idtype_t` / `siginfo_t` in `libposix-process`).

**[ROSEdu](https://github.com/ROSEdu)** - Romanian Open Source Education

- [workshop-github #40](https://github.com/ROSEdu/workshop-github/pull/40) - **merged** - rewrote the Git and
  GitHub workshop so the lab instructions are clearer and students can get started with less setup.

### Currently working on

- **[container-vuln-scanner](https://github.com/lupsalexandra33/container-vuln-scanner)** - multi-scanner
  vulnerability engine for container images, in Go
- **[ctf-writeups](https://github.com/lupsalexandra33/ctf-writeups)** - notes and solutions from CTF challenges

### Selected projects

| Project | What it is | Built with |
| --- | --- | --- |
| [document-scanner](https://github.com/lupsalexandra33/document-scanner) | Computer vision tool for document edge detection, perspective warping, and data extraction | Python, OpenCV, NumPy |
| [async-web-server](https://github.com/lupsalexandra33/async-web-server) | Event-driven HTTP/1.1 server on a single thread, zero-copy `sendfile` and kernel AIO | C, epoll, libaio |
| [mini-shell](https://github.com/lupsalexandra33/mini-shell) | POSIX shell with command execution, I/O redirection and multi-stage pipes | C, POSIX syscalls |
| [chess-game](https://github.com/lupsalexandra33/chess-game) | Full chess implementation with a Swing interface, accounts and saved games | Java, Swing, design patterns |
| [satellite-huffman-tree](https://github.com/lupsalexandra33/satellite-huffman-tree) | Huffman tree built with a min-heap, with encoding, LCA and distance queries | C |
| [numerical-methods-coursework](https://github.com/lupsalexandra33/numerical-methods-coursework) | Markov chains, neural networks, FFT, splines, SVD | MATLAB |
| [asm-coursework](https://github.com/lupsalexandra33/asm-coursework) | Low-level algorithms called from C | x86 assembly, NASM |

---

### Languages

![C](https://img.shields.io/badge/C-00599C?logo=c&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![x86 asm](https://img.shields.io/badge/x86--64%20asm-525252?logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![MATLAB](https://img.shields.io/badge/MATLAB-FF6F00?logo=mathworks&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)

### Frameworks & Tools

![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
