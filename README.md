<div align="center">

# Hi, I'm Alexandra! 👋

*Computer Engineering student at Politehnica University of Bucharest, mostly interested in low-level programming, systems and security.*

[![Email](https://img.shields.io/badge/EMAIL-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:alexandralupsa5@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LINKEDIN-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/lupsalexandra33/)

</div>

### Open source

**[Unikraft](https://github.com/unikraft)** - open-source unikernel SDK

**[catalog-core #91](https://github.com/unikraft/catalog-core/pull/91)** - *in review* - `ruby-hello`
catalog application with Firecracker support (475 LOC, 13 files). Closes
[#25](https://github.com/unikraft/catalog-core/issues/25).

- Root-caused a build failure open since 2021: `lib-ruby` fetches a GitHub branch archive that ships
  `configure.ac` but neither the generated `configure` nor `tool/config.guess` / `tool/config.sub`,
  so `autoconf` regenerates the script and the build then aborts on the missing auxiliary files.
  Proposed fetching the official release tarball from `cache.ruby-lang.org` instead, which ships all three.
- Identified an OpenSSL 3.0 incompatibility in Ruby 2.6's `ext/openssl`, where
  `-Werror=deprecated-declarations` breaks the host build on any distro shipping OpenSSL 3.0.
- Surfaced two further blocking gaps in the Unikraft core: a missing `sys/prctl.h` and undefined
  `idtype_t` / `siginfo_t` in `libposix-process`'s newlib layer.
- Following discussion with maintainers, the integration is being retargeted to Ruby 3.4 on musl.

**Next up:** porting `lib-ruby` to Ruby 3.4 and musl, as agreed with the maintainers.

### Currently working on

- **[container-vuln-scanner](https://github.com/lupsalexandra33/container-vuln-scanner)** - *in progress*
- **[ctf-writeups](https://github.com/lupsalexandra33/ctf-writeups)** - notes and solutions from CTF challenges

### Selected projects

| Project | What it is | Built with |
| --- | --- | --- |
| [chess-game](https://github.com/lupsalexandra33/chess-game) | Full chess implementation with a Swing interface, accounts and saved games | Java, Swing, design patterns |
| [mini-shell](https://github.com/lupsalexandra33/mini-shell) | Bash-like shell with pipes, redirection and job control | C, POSIX syscalls |
| [satellite-huffman-tree](https://github.com/lupsalexandra33/satellite-huffman-tree) | Huffman tree built with a min-heap, with encoding, LCA and distance queries | C |
| [numerical-methods-coursework](https://github.com/lupsalexandra33/numerical-methods-coursework) | Markov chains, neural networks, FFT, splines, SVD | MATLAB |
| [asm-coursework](https://github.com/lupsalexandra33/asm-coursework) | Low-level algorithms called from C | x86 assembly, NASM |
| [document-scanner](https://github.com/lupsalexandra33/document-scanner) | Computer vision tool for document edge detection, perspective warping, and data extraction | Python, OpenCV, NumPy |

---

### Languages

![C](https://img.shields.io/badge/C-00599C?logo=c&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![x86 asm](https://img.shields.io/badge/x86--64%20asm-525252?logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![MATLAB](https://img.shields.io/badge/MATLAB-FF6F00?logo=mathworks&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)

### Frameworks & Tools

![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
