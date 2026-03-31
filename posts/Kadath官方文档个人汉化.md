---
title: Kadath官方文档个人汉化
mathjax: true
excerpt: 作为强大的谱方法偏微分方程求解器，Kadath的社区实在太小，中文社区几乎没有，所有这里提供一个官网的个人汉化，仅供参考
date: 2025-11-27 12:54:17
tags:
  - 数学
  - 物理
  - 工具
categories: 物理
cover: /images/cover/说吧.jpg
---
> 这是我对[Kadath官网](https://kadath.obspm.fr/)的个人汉化，包含安装说明和十几个tutorials，仅供参考。

>由于译者水平不足，部分觉得中文描述不够准确的词会给出原词

# Home #
Kadath 是一个在理论物理学背景下实现谱方法的程序库。
该程序库是完全并行的，但也可以安装串行版本（对于实际问题，其运行速度会相当慢）。
该程序库使用 C++ 编写。
Kadath 是一个遵循 [GNU 通用公共许可证](https://www.gnu.org/licenses/gpl.html) 的自由软件。

关于该工具的详细介绍可以在以下文献中找到：[J. Comput. Phys., 229, 3334 (2010)](http://dx.doi.org/10.1016/j.jcp.2010.01.005)

---

程序库的名称参考了 H.P. 洛夫克拉夫特（HP Lovecraft）笔下“伟大者们”（the Great Ones）的神话居所。
> _" There were towers on that titan mountaintop; horrible domed towers in noxious and incalculable tiers and clusters beyond any dreamable workmanship of man; battlements and terraces of wonder and menace, all limned tiny and black and distant against the starry pshent that glowed malevolently at the uppermost rim of sight. Capping that most measureless of mountains was a castle beyond all mortal thought, and in it glowed the daemon-light. "
> 
> ——*The dream-quest of unknown Kadath* by HP Lovecraft

---
# 需要的前置工具 #

## 必要条件 ##

-   **编译器** ：Kadath 使用 C++ 编写。目前，该软件包同时用到了 GNU 和 Intel 编译器。当使用 Intel MKL 库时，需要强制使用 GNU FFTW 软件包。
-   **CMake** ：该程序库的安装需要 [CMake](https://cmake.org/) 工具。[CMake 官网](https://cmake.org/)
-   **Git** ：Kadath 的源代码通过 [Git](https://git-scm.com/) 存储。
-   **LAPACK** ：部分代数运算通过线性代数包（Linear Algebra Package）完成。需要开发版本。[LAPACK 官网](http://www.netlib.org/lapack/)
-   **FFTW3** ：傅里叶变换由 [FFTW 库](http://www.fftw.org/) 计算。需要开发版本。[FFTW 官网](http://www.fftw.org/)
-   **GSL** ：[GNU 科学计算库](http://www.gnu.org/software/gsl/)（Gnu Scientific Library）用于计算特殊函数，例如球贝塞尔函数。需要开发版本。该库随许多 Linux 发行版提供。[GSL 官网](http://www.gnu.org/software/gsl/)

## 并行版本的额外要求 ##

如果您打算使用 Kadath 的并行版本，还需要以下一些额外事项。

-   **MPI** ：并行化通过 MPI 实现。有多种实现可用。
-   **scaLAPACK** ：是 LAPACK 的并行版本。[scaLAPACK 官网](http://www.netlib.org/scalapack/)

## 可选部分 ##

-   **pgplot** ：该库可用于生成一些图形输出。[pgplot 官网](http://www.astro.caltech.edu/~tjp/pgplot/)。可在此处找到其[快速安装指南](http://www.lorene.obspm.fr/pgplot_quick.txt)。
-   **Doxygen** ：自动文档生成工具。[Doxygen 官网](http://www.stack.nl/~dimitri/doxygen/)。

---
# Kadath的安装 #
## 获取源代码

这通过 Git 服务器完成。使用以下命令：
```
git clone https://gitlab.obspm.fr/grandcle/Kadath.git
```
这将在本地计算机上创建一个名为 `Kadath` 的目录。
请注意，目前用户不允许向 Kadath 提交更改。

## 使用 CMake 编译程序库

-   进入 Kadath 仓库目录。
-   创建一个构建目录（例如使用 `mkdir build` 命令）。
-   您可以创建多个构建目录，它们将包含不同编译选项的结果（例如，一个 `build-release` 用于发布版本，另一个 `build-debug` 用于调试版本）。
-   进入构建目录。
-   调用 `cmake (选项) ..`（`CMakeList.txt` 文件位于上级目录 `..` 中）。
-   可用的主要 CMake 选项如下（括号中的值对应默认设置）：
    -   `D_PAR_VERSION = On/Off (On)`：设置为 `On` 以构建程序库的 MPI 并行版本，设置为 `Off` 以构建串行版本。MPI 并行版本需要 ScaLAPack 或 Intel 数学核心库（MKL）。
    -   `DMKL_VERSION = On/Off (Off)`：设置为 `On` 以使用 Intel MKL 库而不是 ScaLAPack。
    -   `DENABLE_GPU_USE = On/Off (Off)`：设置为 `On` 以构建程序库的版本，该版本将在可用时利用 GPU 解决线性问题，基于 MAGMA 库。
    -   `DUSE_CXX_STANDARD_14 = On/Off (Off)`：允许将程序库编译所需的 C++ 标准版本降级到 14，而不是默认的 C++-17。
    -   `DCMAKE_BUILD_TYPE`：指定构建类型（主要是 `Release` 或 `Debug`）。
    -   `DMPI_CXX_COMPILER`：MPI C++ 包装器的路径（当 CMake 未自动检测到时）。
    -   `DMPI_C_COMPILER`：MPI C 包装器的路径（当 CMake 未自动检测到时）。
-   使用 MKL 和 Intel 编译器进行命令行编译的示例：
    ```
    cmake -DCMAKE_BUILD_TYPE=Release -D_PAR_VERSION=On -DMKL_VERSION=On -DMPI_CXX_COMPILER=/shared/apps/intel/compilers_and_libraries_2019/linux/mpi/intel64/bin/mpiicpc -DMPI_C_COMPILER=/shared/apps/intel/compilers_and_libraries_2019/linux/mpi/intel64/bin/mpiicc ..
    ```
-   在 CMake 无法找到某些必需的外部库的情况下，必须通过 `Kadath/Cmake/CMakeLocal.cmake` 文件手动传递它们（通常需要以这种方式提供 fftw 和 scalapack 库）。该目录中提供了一些该文件的模板。
-   一旦 CMake 成功调用，使用 `make` 命令开始编译。

## 编译 `installer.sh` 脚本

还提供了一个 `installer.sh` 脚本，可用于简化安装过程。它必须使用正确的选项调用。
请使用 `installer.sh --help` 命令查看各种可能的选项。

---
# 生成可执行文件 #

某些代码示例（包括并行和串行）可以在 `codes` 目录中找到。最好也使用 `CMake` 来编译这些代码。

*   创建一个目录 `$MY_PROG` 
*   创建一个目录 `$MY_PROG/src` 
*   将各种源文件，如 `myprog1.cpp`、`myprog2.cpp` 等，放入 `$MY_PROG/src` 目录。确保每个 `.cpp` 文件都有其独立的主函数。
*   将模板文件 `tutorial/CMakeLists.txt` 复制到您的目录 `$MY_PROG`
*   编辑 `CMakeLists.txt`：
    *   将“myproject”替换为您的项目名称。
    *   将“myprog\*”替换为您的程序名称。
*   （在终端）调用 `cmake (options) .`（`CMakeLists.txt` 位于当前目录）。与编译程序库使用的选项相比，您必须额外传递两个选项：
    *   `-DKADATH_SOURCES_DIRECTORY` Kadath 仓库的路径。
    *   `-DKADATH_BUILD_DIRECTORY` Kadath 构建仓库的路径。
*   命令行示例：
    ```
    cmake -DCMAKE_BUILD_TYPE=Release -DPAR_VERSION=OFF -DKADATH_SOURCES_DIRECTORY=~/Kadath/ -DKADATH_BUILD_DIRECTORY=~/Kadath/build-seq-release .
    ```
*   然后使用 `make` 命令编译所有程序。也可以使用 `make myprog*` 独立编译它们。如果您更改了源文件的内容，只需执行此步骤即可。
*   您的可执行文件应位于 `$MY_PROG/bin` 目录中。

---
# 操作手册 #

[操作手册](https://kadath.obspm.fr/static/doxygen/index.html)

---
# 使用KADATH的出版物 #

[使用KADATH的出版物](https://kadath.obspm.fr/publis/)

---
# 贡献者 #

[贡献者](https://kadath.obspm.fr/contributors/)

---
# GNU GPL #

[GNU GPL](https://kadath.obspm.fr/gpl)

---
# 不推荐使用的版本 #

还有一个 Kadath 的预优化版本，它比优化版本大约慢四倍。出于历史原因这里提及它。
## 获取源代码 ##

通过 Git 服务器完成。使用以下命令：
```
git clone --branch deprecated https://gitlab.obspm.fr/grandcle/Kadath.git
```
这将在本地计算机上创建一个 Kadath 目录。

## 编译程序库 ##

*   **环境变量**：
    `$HOME_KADATH` 必须设置为 `KADATH` 目录的位置（使用您喜欢的 shell）。

*   **安装**：
    尝试启动其中一个安装脚本（串行版本使用 `install_seq.sh`，并行版本使用 `install_par.sh`）。

*   **查找各种库**：
    Kadath 是使用 Cmake 工具编译的。
    在 `$HOME_KADATH/Cmake` 仓库中，有一些脚本会尝试自动定位所需的库。
    如果失败，可以在文件 `$HOME_KADATH/Cmake/Cmake.local` 中“手动”设置路径。
    可以设置的变量有：
    `GSL_LIBRARIES`、`FFTW_LIBRARIES`、`LAPACK_LIBRARIES`、`SCALAPACK_LIBRARIES`、`PGPLOT_LIBRARIES`
    提供了一些模板，可以通过将它们复制到 `Cmake.local` 来直接使用。
    一旦 `Cmake.local` 设置完毕，启动安装脚本。

*   **结果**：
    应生成两个版本的库（调试版和发布版），存储在 `$HOME_KADATH/lib` 中。
    文档也已生成并存储在 `$HOME_KADATH/doc` 中。

## 生成可执行文件 ##

一些代码示例（包括并行和串行）可以在 `$HOME_KADATH/codes` 中找到。最好也使用 `Cmake` 来编译这些代码。

*   创建一个 `$MY_PROG` 仓库。
*   创建一个 `$MY_PROG/src` 仓库。
*   将各种源文件，如 `myprog1.cpp`、`myprog2.cpp` 等，放入 `$MY_PROG/src` 目录。目前，每个 `*.cpp` 文件都应有其独立的主函数。
*   将模板文件 `$HOME_KADATH/code/Cmakelists.txt` 复制到您的 `$MY_PROG` 仓库。
*   编辑 `Cmakelists.txt`：
    *   将 "myproject" 替换为您的项目名称。
    *   将 "myprog*" 替换为您的程序名称。
*   配置：
    *   对于串行代码类型：
        `cmake -DPAR_VERSION=OFF .`
    *   对于并行版本：
        `cmake -DPAR_VERSION=ON .`
    *   对于调试版本，可以使用以下选项：
        `-DCMAKE_BUILD_TYPE=Debug`
*   然后运行 `make` 来编译所有程序。也可以使用 `make myprog*` 独立编译它们。如果您更改了源文件的内容，只需执行此步骤即可。
*   您的可执行文件应位于 `$MY_PROG/bin` 目录中。

---
# 教程 #
## 教程一：基础 ##
### Hello ###

下载 `Kadath/tutorials` 目录下的 `starter.cpp` 程序，并按照网站上提供的说明生成可执行文件。
此代码不会执行任何与 Kadath 相关的功能，但能够检查您是否正确配置了环境。

### 构建数组 ###

数组 `Array` 是使用模板构建的，可以是任意维度。对于一、二、三维数组，可以使用 `Array` 直接构造函数。
对于任意维度，必须使用 `Dim_array` 类来传递数组的大小。
以下是一些示例：

```cpp
// 一维 int 数组，大小为 4
Array<int> onedint (4) ;

// 二维 double 型数组，大小为 (8x4)
Array<double> twodoubles (8, 4) ;

// 五维 bool 型数组，通过 Dim_array 构建：
Dim_array dimensions(5) ;
// 必须初始化各个维度的编号(The size of the various dimensions must be initialized,译者也不知道怎么翻译更准确，大致就是，维度的顺序)
for (int i=0 ; i<5 ; i++)
    dimensions.set(i) = i+1 ;
Array<bool> multidbool (dimensions) ;
```

### 使用数组

数组是在未初始化(uninitialized)状态下构建的。它们可以被赋予整个数组的单个值，或通过 `set` 函数逐个元素地访问。
如果维度是任意的，则必须通过一个名为 `Index` 的类来访问。
只读访问只需要通过 `operator()` 
```cpp
// 1D 数组
for (int i=0 ; i<4 ; i++)
    onedint.set(i) = i ;
cout << onedint << endl ; // 打印整个数组的代码在这里

// 2D 数组，所有元素值为同一个值
twodoubles = 2.3 ;
// 打印特定的一个元素
cout << twodoubles(0, 2) << endl ;

// 5 维数组：
Index pos(dimensions) ;
// 默认情况下，它指向第一个元素
// 让index指向第二维
pos.set(2) = 1 ;
cout << pos << endl ;
// 此时 pos 指向数组的一个特定元素
multidbool = false ; // 所有元素都为 false
multidbool.set(pos) = true ; // 除了这个...
```

### 遍历数组

索引有一个成员函数 `inc`，它将给索引增加一个单位1。如果结果仍在 `Array` 中，则返回 `TRUE`；如果不在（即已到达 `Array` 的末尾），则返回 `FALSE`。它广泛用于遍历数组的所有元素。

```cpp
// 将索引设置为第一个索引
pos.set_start() ;
// 循环
do {
    if (multidbool(pos)) {
        cout << "找到 True 值于 " << endl ;
        cout << pos << endl ;
    }
} while (pos.inc()) ;
```

---
## 教程二：空间 ##

Kadath 库中的一系列 `Space` 类用于描述各种数值域(numerical domains)，每个域都包含了自身的几何结构信息与所使用的谱点数量。此外 `Space` 对象还定义了不同域之间的相互关系。

### 设置空间 ###

构造函数的参数取决于所考虑的空间类型，但有些参数是通用的：

*   域（domain）的数量
*   基函数的类型（切比雪夫或勒让德）
*   每个域中的谱点数

**警告**：
由于使用了 FFTW，点的数量不能任意选取，它取决于谱基。经验法则：对于变量 phi ，使用形如 $2^m 3^n 5^p$ 的整数；对于其他坐标，使用形如 $2^m 3^n 5^p+1$ 的整数。例如，在径向方向上，11, 13, 17, 21, 25, 33 是可接受的数字。

```cpp
// 球形空间的示例
// 由多个三维球形域构成

// 3D
int dim = 3 ;

// 谱点数设置
Dim_array res (dim) ;
res.set(0) = 13 ; // r 方向的谱点数
res.set(1) = 5 ; // theta 方向的谱点数
res.set(2) = 4 ; // phi 方向的谱点数

// 中心点的绝对坐标
Point center (dim) ;
for (int i=1; i<=dim ; i++)
    center.set(i) = 0 ;

// 域的数量和域的边界
int ndom = 4 ;
Array<double> bounds (ndom-1) ;
bounds.set(0) = 1 ; bounds.set(1) = 2 ; bounds.set(2) = 4 ;

// 切比雪夫或勒让德
int type_coloc = CHEB_TYPE ;

// 球形空间构造函数
Space_spheric space(type_coloc, center, res, bounds) ;
cout << space << endl ;
```

### 访问器 ###

可以通过 `get_domain` 函数访问单个域，该函数返回一个指针。
这些域有多种函数可用于获取与每个域相关的各种信息。例如，可以获取配置点（collocation points）数、系数数量、每个配置点处的半径等。

```cpp
// 打印域 0 中点的数量
cout << space.get_domain(0)->get_nbr_points() << endl ;

// 打印域 1 中系数的数量
cout << space.get_domain(1)->get_nbr_coefs() << endl ;

// 返回域 0 的半径
cout << space.get_domain(0)->get_radius() << endl ;

// 返回域 1 的 X 坐标
cout << space.get_domain(1)->get_cart(1) << endl ;
```

---
## 教程三：标量场 ##

本节教程介绍标量场的使用。
### 构造与赋值

标量场是基于 `Space` 构建的。可以使用各个 `Domain` 中可用的方法（主要是半径和类笛卡尔坐标）为其赋予显式表达式。

请注意，Kadath 并不主要使用解析表达式。这些表达式可能需要相对简单并且仅用作方程组数值求解的初始猜测值。

```cpp
// 假定一个球形空间已被构造
// 如果需要，获取域的数量
// int ndom = space.get_nbr_domains() ;

Scalar func (space) ;

// 在域 0 中置入 1-r^2
func.set_domain(0) = 1 - pow(space.get_domain(0)->get_radius(),2) ;
// 在其他域中置入 1/r
for (int d=1; d<ndom ; d++)
    func.set_domain(d) = 1/space.get_domain(d)->get_radius() ;

// 打印每个配置点上的值
cout << "标量函数 func " << endl ;
cout << func << endl ;
```

### 处理无穷大量

Kadath 可以在标准运算中用到无穷大。例如，计算直到无穷远处的 $1/r$ 是可以的，因为其结果值为零。

然而，当程序库无法正确计算结果时，更复杂的情况可能会导致 nan（非数字）量的出现。在这种情况下，需要使用诸如 `set_val_inf` 之类的函数手动传入正确的值。

```cpp
// 使用与之前相同的标量
// 在外部域中置入 r * exp(-r^2/10)
for (int d=1; d<ndom ; d++)
    func.set_domain(d) = *space.get_domain(d)->get_radius()
    * exp(- *space.get_domain(d)->get_radius() * *space.get_domain(d)->get_radius() /10.) ;

// 无穷远处出现 Nans
cout << "无穷远处的 Nans" << endl ;
cout << func(ndom-1) << endl ;

// 手动设置无穷远处的正确值
func.set_val_inf(0.) ;

// 不再有 Nans
cout << "Nans 已被移除" << endl ;
cout << func(ndom-1) << endl ;
```

### 设置基 ###

此时，标量场不包含任何关于基底的信息，这限制了其可能性。有另一个教程专门介绍基。这里我们假设基是标准的，并直接使用：

```cpp
// 为标量场设置标准基
func.std_base() ;
```

### 访问场的值 ###

已经使用过的 `cout` 函数会打印场在配置点上的值和/或其谱系数，具体取决于哪个量已被计算。

然而，我们通常需要在给定点（即非配置点）上计算值。这可以通过使用 `val_point` 函数来完成，该函数接受一个 `Point` 作为参数。`Point` 类仅包含点的绝对坐标（通常是 X,Y,Z）。

```cpp
// 在三维空间中定义一个 Point
Point M (3) ;

// 设置其坐标
M.set(1) = 2.93 ; // Y 坐标
M.set(2) = -3.19 ; // Y 坐标
M.set(3) = 1.76 ; // Z 坐标

// 打印标量场在 M 点的值
cout << "点 M 是 " << M << endl ;
cout << "场在 M 点的值 " << func.val_point(M) << endl ;
```

### 对标量场进行操作 ##

利用谱系数，Kadath 就可以对标量场执行各种操作，例如求其径向导数或将其乘以半径。在后一种情况下，操作是在系数空间中执行的，这可以防止出现 nan 量并给出正确的值。我们可以通过调用 `coef_i` 来强制代码计算在配置点上的值。

```cpp
// 计算径向导数
Scalar derr (func.der_r()) ;
cout << "径向导数在 M 点的值 " << derr.val_point(M) << endl ;

// 使用乘以 r 的操作
Scalar multr (func.mult_r()) ;
// 强制代码计算在配置点上的值
multr.coef_i() ;

// 无穷远处没有出现 nans
cout << "最后一个域中的值 " << endl ;
cout << multr(ndom-1) << endl ;
```

在最后一个例子中，您可能会注意到最后一个配置点上的值并不完全为零，尽管它本应为零。然而，当径向点的数量增加时，这个值会指数级地趋向于零（您可以轻松地验证这一点）。这表明，从数值的角度来看，我们的计算是正确的。

---
## 教程四：谱基Spectral Basis

本节教程给出了一些关于谱基的基础知识。

### 标准基 ###

函数 `std_base` 为标量场设置标准基。对于大多数空间，此基假设场可以展开为 $x^m y^n z^{2p}$ 形式的多项式（即类笛卡尔坐标的多项式）。

这种形式确保了各处的正则性（例如在原点或球坐标系的轴上）。还可以注意到，这里假设了关于 $z=0$ 平面的偶对称性。

每个域都可以访问基，结果以多个数组的形式给出。例如，在球形域中，三个坐标是 r、theta 和 phi，系数以相反的顺序取用，首先是关于 phi 的，然后是关于 theta 的，最后是关于 r 的。因此，phi 只有一个基，theta 有一个一维的基数组（每个 phi 索引对应一个），而 r 有一个二维的基数组（每个角向索引对对应一个）。各种基以整数形式存储，其转换关系可以在文件 `spectral_basis.hpp` 中找到。

```cpp
// 假设标量场 func 已在此前计算过（见教程 3）
// 将基设置为标准基
func.std_base() ;

// 打印域 1（第一个壳层）中的基
cout << "域 1 中的基" << endl ;
cout << func(1).get_base() << endl ;

// 结果解读如下
// 变量 2 是 phi，只有一个基，标记为 4，它是一个完整的正弦和余弦序列
// 变量 1 是 theta，一个基的数组，值为 6 和 10。
// 它对应于偶余弦或奇正弦，具体取决于 phi 的索引。
// 变量 0 是 r，一个二维数组，值为 1
// 它对应于切比雪夫多项式，与角度的索引无关。

// 打印域 0（核心）中的基
cout << "域 0 中的基" << endl ;
cout << func(0).get_base() << endl ;

// 由于原点的正则性条件，它与前一种情况不同。
// 这意味着关于 r 的基是偶数或奇数切比雪夫多项式。
```

### 谱基与计算 ###

当场被操作时，Kadath 会尝试跟踪其基。例如，在对两个场求和时，它会检查它们是否具有相同的基，并将其赋给结果。在对场进行乘法运算时，代码通常也能够猜测出正确的基。在调用像导数或乘以 r 这样的算子时，程序库也能够计算出结果的基。

然而，在某些情况下，基无法自动获取。例如，如果对一个量取余弦，它没有自然定义的基（切比雪夫多项式的余弦不是切比雪夫多项式）。在这种情况下，必须使用像 `std_base` 这样的函数手动设置基。

**重要规则**：除非您确实需要，否则不要调用 `std_base` 并尝试理解为什么代码会丢失对谱基的跟踪。

```cpp
// 场的组合
Scalar f1 (2*func + func*func) ;
// 基是已知的，并且是标准基：
cout << "核心中 2*f + f*f 的基" << endl ;
cout << f1(0).get_base() << endl ;
// 它是标准基

// 求导
Scalar der (func.der_r()) ;
cout << "核心中 f' 的基" << endl ;
cout << der(0).get_base() << endl ;
// 它不是标准基；r 的宇称发生了变化

// 余弦算子
Scalar test (cos(func)) ;
cout << "cos(f) 的基未定义" << endl ;
cout << test(0).get_base() << endl ;
```

### 非标准基的示例 ###

对于标量，标准基假设关于 $z=0$ 是偶对称的。因此，如果定义一个奇函数，`std_base` 将会引起问题。Kadath 中还有许多其他函数可以设置谱基。问题在于选择正确的那个。

例如，对于形式为 $x^m y^n z^{2p+1}$ 的函数，应该使用 `std_anti_base`。

```cpp
// 定义一个标量场，在核心处为 z，在其他地方为 z/r^2
Scalar odd (space) ;
odd.set_domain(0) = space.get_domain(0)->get_cart(3) ; // z 坐标
for (int d=1 ; d<ndom ; d++)
    odd.set_domain(d) = space.get_domain(d)->get_cart(3)
    / *space.get_domain(d)->get_radius() / *space.get_domain(d)->get_radius() ;
// 在无穷远处设置正确的值
odd.set_val_inf(0.) ;
// 尝试使用 std_base()
odd.std_base() ;
// 使用 val_point 将数值与解析值进行比较
Point M(3) ;
M.set(1) = 2.32 ;
M.set(2) = 1.32 ;
M.set(3) = 1.98 ;
double rr = sqrt(M(1)*M(1)+M(2)*M(2)+M(3)*M(3)) ; // 获取半径：检查它不在核心中
cout << "解析值 = " << M(3) /rr /rr << endl ;
cout << "错误的数值 = " << odd.val_point(M) << endl ;

// 设置正确的谱基：
odd.std_anti_base() ;
odd.set_in_coefs() ; // 需要清除先前计算的（错误的）系数。
cout << "正确的数值 = " << odd.val_point(M) << endl ;
```

---
## 教程五：方程组系统 ##

本节教程介绍 Kadath 的偏微分方程（PDE）求解器。

### `System_of_eqs` 构造函数 ###

`System_of_eqs` 是 Kadath 库的主要对象之一。它用于描述一个偏微分方程组并对其进行求解。它仅通过 `space` 以及可能使用的域来构造。（不指定域意味着整个空间，也可以指定单个域或一定范围的域）。

```cpp
// 假设一个 space 是已知的（见教程 1）
// 如果需要，获取域的数量
int ndom = space.get_nbr_domains() ;

// 构造函数
System_of_eqs syst (space, 1, ndom-1) ;
// 这里将在域 1 到 ndom-1 中求解方程（即除了域 0 之外的所有地方）
```

### 定义未知量 ###

需要告知求解器系统的未知量是什么。它们可以是数字、标量场或广义张量。首先，我们将考虑一个简单的标量场。该场必须预先用正确的谱基定义好。它的值将被求解器用作初始猜测。使用函数 `add_var`（意为添加可变场，即一个允许求解器修改的场）。

```cpp
// 构建一个标量场
Scalar field (space) ;
field = 1 ;
field.std_base() ;

// 该场是一个未知量
syst.add_var ("F", field) ;
// 该字符串是系统将用来指代此场的名称。
```

### 传递常数 ###

常数是求解器将会使用但不会更改其值的场或数字。与未知量一样，它们必须预先被定义好。使用函数 `add_cst`。

```cpp
// 定义一个常数，即第一个域的半径
Index pos (space.get_domain(1)->get_nbr_points()) ; // 域 1 上的index
double rad = space.get_domain(1)->get_radius()(pos) ;
cout << "第一个壳层的内半径是 " << rad << endl ;

// 这个数字是系统的一个常数
syst.add_cst ("a", rad) ;
// 该字符串是系统将用来指代此常数的名称。
```

### 主体方程 ###

现在可以开始实现想要求解的方程。在这个特定的教程中，我们想在整个计算域中求解 $\text{Lap}(F) = 0$。这是一个二阶方程，我们必须使用函数 `add_eq_inside`（因为它需要两个边界条件，一个内边界和一个外边界，本身也是二阶方程）。

```cpp
// 方程在每个域中都是相同的
for (int d=1 ; d<ndom ; d++) // 遍历域
    syst.add_eq_inside (d, "Lap(F)=0") ;
// Lap 是 Kadath 的一个保留字，表示平直拉普拉斯算子，而 F 是我们之前定义的。
```

### 边界条件

主方程是二阶的，因此需要一个内边界条件和一个外边界条件。使用 `add_eq_bc`，它与 `add_eq_inside` 的不同之处在于它不仅需要域的编号，还需要描述所涉及的边界。这里我们将使用 `INNER_BC` 和 `OUTER_BC`，两个 Kadath 内置常数，分别描述内边界和外边界。

```cpp
// 内边界条件
syst.add_eq_bc (1, INNER_BC, "dn(F) + 0.5*F/a = 0") ;
// 这是一个罗宾（Robin）边界条件
// dn 代表相对于边界的法向导数（在这种情况下是 d/dr）

// 外边界条件
syst.add_eq_bc (ndom-1, OUTER_BC, "F-1") ;
// 场在空间无穷远处为 1
```

### 匹配条件

最后，需要说明解及其径向导数在数值边界上是连续的。这通过函数 `add_eq_matching` 来完成，它与 `add_eq_bc` 类似。

```cpp
// 遍历域之间的所有边界
for (int d=1 ; d<ndom-1 ; d++) {
    // 域 d 和 d+1 之间场的匹配
    syst.add_eq_matching (d, OUTER_BC, "F") ;
    // 域 d 和 d+1 之间场的法向导数的匹配
    syst.add_eq_matching (d, OUTER_BC, "dn(F)") ;
}
```

### 检查方程

此时，可以检查方程是否被满足。可以使用 `check_equations`。它将给出一个数组，其中包含传递给系统的各个方程的误差。

```cpp
Array<double> errors (syst.check_equations()) ;
// 验证方程的数量，即 errors 的大小
int neq = errors.get_size(0) ;
cout << "系统有 " << neq << " 个方程。" << endl ;
// 打印误差，当它们“大”的时候
for (int n=0 ; n<neq ; n++)
    if (fabs(errors(n)) > 1e-10)
        cout << "方程 " << n << " : 误差 " << errors(n) << endl ;
// 在本例中，只有内边界条件不被我们的初始猜测所满足
```

### 启动求解器

解是通过牛顿-拉夫逊（Newton-Raphson）算法迭代求解的。调用的函数是 `do_newton`。它接受一个误差阈值作为输入，并给出一个当前误差作为输出。如果误差小于阈值，它返回 `TRUE`，否则，它执行一次牛顿-拉夫逊算法的迭代并返回 `FALSE`。

在进行迭代之前，代码将检查未知量（未知场的系数）的数量是否与方程的数量一致，用户必须给出正确数量的方程。

```cpp
// 定义阈值
double prec = 1e-8 ;
// 当前误差
double error ;
// 迭代结束了吗？
bool endloop = false ;

while (!endloop) {
    endloop = syst.do_newton(prec, error) ;
}
// 在第一次调用时，误差很大，因此求解器执行一次迭代，endloop 仍为 false。
// 在第二次调用时，误差小于阈值，因此 endloop 为 true，从而结束循环。
// 在该示例中，问题是线性的，因此在一次迭代中就收敛了。
```

### 检查解 ###

标量场已被代码修改，应与正确的解匹配。可以通过在计算域中取一个随机点来进行检查。

```cpp
// 随机点
Point MM(3) ;
MM.set(1) = 1.3873 ;
MM.set(2) = -0.827 ;
MM.set(3) = 0.962 ;
// 数值解
double numerical = field.val_point(MM) ;
// 解析解
// 获取半径
double rr = sqrt(MM(1)*MM(1)+MM(2)*MM(2)+MM(3)*MM(3)) ;
double analytic = 1 + rad / rr ;
cout << "数值解 = " << numerical << endl ;
cout << "解析解 = " << analytic << endl ;
cout << "相对误差 = " << fabs(numerical-analytic) / numerical << endl ;
```

---
## 教程六：使用定义 ##

本节教程介绍如何在 Kadath PDE求解器中使用定义。

### Test Problem ###

我们将使用与教程五中相同的物理问题，不过这次要处理那个场的对数形式。为此，进行以下更改：

*   体方程变为 $\Delta P + \partial_i P \partial^i P = 0$
*   内边界条件为 $\mathrm{d}r(P) + 1/(2a) = 0$
*   外边界条件为 $P=0$

这样，我们就成功将一个线性问题转换为了非线性问题。

### Kadath 中的定义 ###

在方程组中，一个表达式经常会多次出现。用户可以将其作为一个定义（definition）传递给求解器，而无需每次都用变量和常量重写它。这通过函数 `add_def` 完成。

```cpp
// 假设已经定义了一个方程组 syst 和一个标量场 field (如教程 5 所示)。

// 将项 partial_i P partial^i P 作为一个定义传入
syst.add_var ("P", field) ;
syst.add_def ("dP2 = scal(grad(P), grad(P))") ;

// scal 是一个保留字，表示平直空间标量积
// grad 是一个保留字，表示平直空间梯度
```

将定义传递给系统后，就可以在所有 Kadath 方程中使用它的名称。

```cpp
// 体方程
for (int d=1 ; d<ndom ; d++)
    syst.add_eq_inside (d, "Lap(P) + dP2 = 0") ;

// 内边界条件
syst.add_eq_bc (1, INNER_BC, "dn(P) + 0.5/a = 0") ;

// 外边界条件
syst.add_eq_bc (ndom-1, OUTER_BC, "P=0") ;
```

写好场上的匹配条件后，就可以像教程 5 那样求解系统并检查分辨率。您会注意到，由于系统是非线性的，牛顿-拉弗森（Newton-Raphson）求解器需要数步才能收敛。

### 为何使用定义？ ###

主要有两个原因：

*   首先，它使系统方程的书写更清晰，因为人们无需用变量和常量显式地写出所有内容。
*   其次，定义的数值在每次迭代中只计算一次，而不是在方程中每次遇到时都计算。这可以在计算时间上带来显著的提升。

例如，假设一个场的径向导数在方程中多次出现。如果您只写作 $\mathrm{d}r(P)$，Kadath 会在每次遇到该项时都计算一次这个导数。然而，如果您传入一个包含该导数的定义，它将只被计算一次（在每次迭代中），其值将被存储在定义中，并在需要时直接复制其值。

### 使用定义进行计算 ###

Kadath 允许用户使用 `give_val_def` 函数来覆盖一个定义的值。它以 `Tensor` 的形式返回定义的当前值（参见教程 7）。在定义未知的区域，其值将被置为零。

```cpp
// 让我们在求解系统后，计算第一个壳层中的 P^2
syst.add_def (1, "Psquare = P^2") ;
// 该定义仅在第一个壳层中有效。

// 以张量形式覆盖其值，该张量将被转换为一个标量场
Scalar P2 (syst.give_val_def("Psquare")) ;

// 打印 P2，它仅在第一个壳层中非零
cout << P2 << endl ;

// 与直接计算的平方值进行比较
Scalar P2direct (field*field) ;
cout << P2direct() << endl ;
```

当然，在这个例子中，在 `System_of_eqs` 之外进行直接计算会更容易，但情况并非总是如此。

---
## 教程七：张量 ##

本节教程涉及矢量和更高阶的张量。

### 张量基 ###

在定义张量之前，需要描述其所使用的张量基（tensorial basis）。该对象不同于谱基（spectral basis），这两个概念不应混淆。在每个定义域中，张量基描述了给定张量的坐标所依据的基底。在 Kadath 中，主要有两种：

*   由保留字 `CARTESIAN_BASIS` 表示的笛卡尔基。
*   由保留字 `SPHERICAL_BASIS` 表示的标准正交球坐标基。

即便在球坐标下工作，也并不是不能使用笛卡尔基，这只是意味着一个矢量 $V_i$ 将由其分量 $Vx$, $Vy$ 和 $Vz$ 来描述，其中每个分量都作为 $r$, $\theta$ 和 $\phi$ 的函数给出。

不同的张量基也可以在不同的定义域中使用。其中一些基对于某些空间（space）是不可用的（例如，在双球空间中不能使用球坐标基）。

```cpp
// 假设我们已经有了一个球坐标空间 space 及其定义域数量 ndom 
// 使用笛卡尔基构造
Base_tensor basis_cart (space, CARTESIAN_BASIS) ;
// 构造器使得各处都使用相同的张量基

// 在第一个壳层中设置一个标准正交球坐标基
Base_tensor basis_mixed (space, CARTESIAN_BASIS) ;
basis_mixed.set_basis(1) = SPHERICAL_BASIS ;
cout << "The mixed tensorial basis is " << endl ;
cout << basis_mixed << endl ;
```

### 构造矢量场 ###

除了标量场，矢量场就是最简单的张量场。它们由一个 `Space` 构造。必须指明其表示是协变的（保留字 `COV`）还是逆变的（保留字 `CON`）。因此，它可以描述真正的矢量或 1-形式（1-form）。张量基也必须被指定。

```cpp
// 构造一个矢量
Vector vecU (space, CON, basis_cart) ;
```

### 矢量赋值与谱基 ###

矢量的分量通过函数 `set` 进行赋值，该函数返回一个给定的分量。请注意，分量的索引范围是从 1 到维度大小（而不是从 0 开始）。

与标量场一样，我们必须提供谱基。它取决于所使用的空间、张量基和所考虑的分量。

例如，对于笛卡尔坐标下的一个矢量，函数 `std_base` 假定该矢量是某个标量场的梯度。由此可知，x 和 y 分量相对于平面 z=0 是对称的，而 z 分量是反对称的，从而导致不同的基。

```cpp
// 在核中设置 (x,y,z)
for (int cmp=1 ; cmp<=3 ; cmp++)
    vecU.set(cmp).set_domain(0) = space.get_domain(0)->get_cart(cmp) ;

// 为其他域设置 (x/r, y/r, z/r)
for (int d=1 ; d<ndom ; d++)
    for (int cmp=1 ; cmp<=3 ; cmp++)
        vecU.set(cmp).set_domain(d) = space.get_domain(d)->get_cart_surr(cmp) ;

// 设置适当的谱基（这里是标准基）
vecU.std_base() ;

// 在核中打印谱基
for (int cmp=1 ; cmp<=3 ; cmp++) {
    cout << "Basis of cmp " << cmp << " in the nucleus: " << endl ;
    cout << vecU(cmp)(0).get_base() << endl ;
}
```

### 变换张量基 ###

在某些情况下，可以通过调用以下函数来变换张量基：

*   `change_basis_spher_to_cart` 从标准正交球坐标基变为笛卡尔基。
*   `change_basis_cart_to_spher` 执行相反的操作。

谱基也会以一致的方式相应更改。

### 一般张量 ###

适用于矢量的情况，对于更高阶的张量也基本成立。唯一复杂之处在于，必须将张量的阶（valence）以及所有索引的类型传递给构造器。

```cpp
// 构造一个二阶张量，两个索引都是逆变的
Tensor Tone (space, 2, CON, basis_cart) ;
cout << Tone << endl ; // 此时分量的值尚未定义

// 一个三阶张量，具有 CON, CON, CON 索引
int valence = 3 ;
Array<int> type_indices (valence) ;
type_indices.set(0) = CON ;
type_indices.set(1) = CON ;
type_indices.set(2) = CON ;
Tensor Ttwo (space, valence, type_indices, basis_cart) ;
```

### Accessors ###

对于低阶张量（即阶数低于 4），accessors通过逐个给出索引来工作。

对于更高阶的张量，需要使用 `Index` 类（参见教程一）。请注意，在这种情况下，索引应从 0 到 dim-1（因为使用的是 `Array` 描述和 `Index`）。

```cpp
// 直接访问
Ttwo.set(1,2,2) = 1 ; // 将 (x,y,y) 分量设置为 1

// 使用 Index 进行访问
Index indices (Ttwo) ;
indices.set(0) = 2 ; indices.set(1) = 0 ; indices.set(2) = 0 ; // 对应于 (z,x,x)
Ttwo.set(indices) = 2. ;

cout << Ttwo << endl ; // 仅定义了两个分量
```

---
## 教程八：在方程组中使用张量 ##

本教程展示了如何在 `System_of_eqs` 中使用张量。

### 张量作为变量或常量 ###

将张量作为未知场或常数场传递时，无需传递其索引。库会从张量对象中推断出正确的阶（valence）和索引类型。

```cpp
// 假设已定义一个球坐标空间（为安全起见，在 theta 上取 9 个点，在 phi 上取 8 个点）
// 假设有两个先前定义的张量：vecU（矢量）和 tenT（二阶协变张量）

// 方程组仅在定义域 1 中
System_of_eqs syst (space, 1) ;
// 将 U 作为未知场传入
syst.add_var ("U", vecU) ;
// 将 T 作为常数传入
syst.add_cst ("T", tenT) ;
```

### 在定义中使用张量 ###

在定义中使用张量时，必须为索引提供一个名称。协变索引由 `_` 表示，逆变索引由 `^` 表示。如果索引类型与张量场的定义不一致，且度规已被定义（参见教程 9），则会使用度规来操纵索引。张量的标准运算均可用，如缩并、张量积等。当一个索引名称重复出现时，将使用爱因斯坦求和约定（进行缩并）。

```cpp
// 张量积
syst.add_def ("TV_ijk = T_ij * U^k") ;

// 带缩并的张量积
syst.add_def ("Contract_i = T_ij * U^j") ;

// 转置
syst.add_def ("Transpose_ij = T_ji") ;

// 由于没有定义度规，索引操纵会产生错误
//syst.add_def ("Ucov_i = U_i") ;

// 各种定义可以通过 give_val_def 访问
// 例如用于打印
cout << syst.give_val_def("Contract") << endl ;
```

### 用张量求解方程 ###

张量在方程中的使用方式与在定义中相同。

**要点** 目前，尚无法在核（nucleus）中使用标准正交球坐标基（由于原点处的正则性条件存在困难）。除此之外，所有其他情况都应正常工作（例如各处都使用笛卡尔基，或在避开原点的定义域中使用球坐标基）。

```cpp
// 将只使用 syst 在定义域 1 中求解

// 为内边界条件定义一个张量（使用 vecU 初始值的两倍）
Vector vecInner (2*vecU) ;
syst.add_cst ("I", vecInner) ;

// 任意的内边界条件
syst.add_eq_bc (1, INNER_BC, "U^k= I^k") ;

// 体方程
syst.add_eq_inside (1, "lap(U^k) = 0") ;

// 外边界条件
syst.add_eq_bc (1, OUTER_BC, "U^k= 0") ;


// 牛顿-拉弗森求解器
double prec= 1e-8 ;
double error ;
bool endloop = false ;
while (!endloop) {
    endloop = syst.do_newton(prec, error) ;
}

// 问题是线性的，一步收敛。
// 可以打印解
for (int cmp=1 ; cmp<=3 ; cmp++) {
    cout << "Component " << cmp << endl ;
    cout << vecU(cmp)(1) << endl ;
}

// 此时 vecU 不再是 vecInner/2（前者已被求解器修改）。
```

---
## 教程九：平直度规 ##

本节教程展示如何使用平直度规。

### 定义 ###

平直度规仅由 `Space` 和分解所用的张量基构造。

这些对象被设计用于 `System_of_eqs` 中，因此在这一点上能做的事情不多。

```cpp
// 假设已定义一个球坐标空间（为安全起见，在 theta 上取 9 个点，在 phi 上取 8 个点）
// 一个笛卡尔张量基
Base_tensor basis_cart (space, CARTESIAN_BASIS) ;
Metric_flat fmet_cart (space, basis_cart) ; // 关联的平直度规

// 在标准正交球坐标基中的情况相同
Base_tensor basis_spher (space, SPHERICAL_BASIS) ;
Metric_flat fmet_spher (space, basis_spher) ; // 关联的平直度规
```

### 将度规关联到系统 ###

`System_of_eqs` 和 `Metric` 之间的关联是通过调用度规的一个函数 `set_system` 来完成的。一旦完成此操作，就可以在系统中使用许多附加功能，例如操纵张量索引和协变导数。

```cpp
// 系统仅在第一个壳层中
System_of_eqs syst (space, 1) ;

// 使用标准正交球坐标基
fmet_spher.set_system (syst, "f") ;
// 该字符串表示系统识别度规所用的名称

// 恢复并打印度规的逆
syst.add_def ("inv^ij = f^ij") ;
cout << syst.give_val_def("inv") << endl ;

// 假设已定义一个逆变矢量 vecU
// 将其用作常数
syst.add_cst ("U", vecU) ;

// 可以操纵其索引
syst.add_def ("Ucov_i = U_i") ;

// 可以计算标量积（应为 1）
syst.add_def ("product = U_i * U^i") ;
cout << syst.give_val_def("product") << endl ;

// 协变导数
syst.add_def ("der_i j = D_i U^j") ;
cout << syst.give_val_def("der") << endl ;
```

---
## 教程十：一般度规

本节教程介绍如何使用一般度规。

### `Metric_tensor` 类 ###

为了处理度规，必须使用一种特殊的 `Metric_tensor` 类型。它是一个二阶对称张量。两个指标的类型相同，但可以是协变或逆变，因此该类可以描述度规或其逆。

```cpp
// 假设已定义一个球坐标空间（为安全起见，在 theta 上取 9 个点，在 phi 上取 8 个点）
// 张量基
Base_tensor basis (space, CARTESIAN_BASIS) ;
Metric_tensor gmet (space, CON, basis) ;

// 各处赋值为平直度规
for (int i=1 ; i<=3 ; i++) {
    gmet.set(i,i) = 1. ;
    for (int j=i+1 ; j<=3 ; j++)
        gmet.set(i,j) = 0 ;
}

// 定义域 1 中非平凡内容
for (int i=1 ; i<=3 ; i++)
    for (int j=i ; j<=3 ; j++)
        gmet.set(i,j).set_domain(1) =
        gmet(i,j)(1) + space.get_domain(1)->get_cart(i)*space.get_domain(1)->get_cart(j) ;

// 在此情况下的标准基
gmet.std_base() ;
cout << gmet << endl ;
```

### 使用常数度规 ###

常数度规由 `Metric_const` 类描述。常数意味着它一次性给出，并且系统不允许更改它。在这方面，它的工作方式与使用 `add_cst` 定义的常数场相同（参见教程 5）。显然，这不意味着该度规在空间中是常数。

它的工作方式与教程 9 中的平直度规相同。

```cpp
// 构造一个常数度规
// 数值包含在一个可以是协变或逆变的 Metric_tensor 中。
Metric_const met (gmet) ;

// 将其传递给系统
System_of_eqs syst (space, 1) ;
met.set_system (syst, "g") ;

// 可以获取联络系数（保留字 Gam）
syst.add_def ("Christo_ij^k = Gam_ij^k") ;
cout << syst.give_val_def("Christo") << endl ;

// 也可以获取里奇张量（保留字 R）
syst.add_def ("Ricci_ij = R_ij") ;
cout << syst.give_val_def("Ricci") << endl ;
```

### 度规作为未知量

度规通常是给定但作为物理问题一部分的情况，这意味着它是一个求解器试图寻找的未知场。在这种情况下，必须使用 `Metric_general` 类。它的工作方式与 `Metric_const` 相同，只是度规现在被视为一个变量场（参见教程 5）。

求解方程组将改变用于定义度规的 `Metric_tensor`。

```cpp
// 构造内边界和外边界的场
Metric_tensor ginner (gmet) ; // 包含 gmet 的初始值
// 无需调用 std_base 
Metric_tensor gouter (space, COV, basis) ;
for (int i=1 ; i<=3 ; i++) {
    gouter.set(i,i) = 1. ;
    for (int j=i+1 ; j<=3 ; j++)
        gouter.set(i,j) = 0 ;
}
gouter.std_base() ;

// 构造一个未知度规
// 初始数值包含在一个 Metric_tensor 中。
Metric_general metgen (gmet) ;

// 将其传递给一个新系统
System_of_eqs systtwo  (space, 1) ;
metgen.set_system (systtwo, "g") ;

// 将场 ginner 和 gouter 作为常数传入
systtwo.add_cst ("gin", ginner) ;
systtwo.add_cst ("gout", gouter) ;

// 随机方程
systtwo.add_eq_bc (1, INNER_BC, "g_ij = gin_ij") ;
systtwo.add_eq_inside (1, "lap(g_ij) = 0") ;
systtwo.add_eq_bc (1, OUTER_BC, "g_ij = gout_ij") ;

// 牛顿-拉弗森求解器
double prec = 1e-8 ;
double error ;
bool endloop = false ;
while (!endloop) {
    endloop = systtwo.do_newton(prec, error) ;
}

// 解包含在 gmet 中
// 可以检查它与包含 gmet 初始值的 ginner 是否不同
for (int i=1 ; i<=3 ; i++)
    for (int j=i ; j<=3 ; j++)
        cout << "Diff in comp " << i << ", " << j << " : " << diffmax(gmet(i,j)(1), ginner(i,j)(1)) << endl ;
```

---
## 教程十一：在方程组中处理分量 ##

本节教程关注方程组中分量的管理。

### 问题的提出 ###

有时，需要对场的不同分量使用不同的方程。这可以通过在将相关方程传递给 `System_of_eqs` 时，指定要使用的分量来实现。

有时库也会丢失对某些对称性的追踪。例如，假设未知量是一个度规。它是一个对称张量，因此会产生一组 6 个未知分量。然而，当方程很复杂时，Kadath 可能会丢失对称性信息，从而将其视为一个一般张量（因此有 9 个分量）。这将导致不一致。为了处理这种情况，可以强制代码只考虑“正确”的分量。

```cpp
// 假设已定义一个球坐标空间（为安全起见，在 theta 上取 9 个点，在 phi 上取 8 个点）
// 假设一个 Metric_tensor gmet 已被定义
// 假设有两个 Metric_tensor ginner 和 gouter 用于边界条件（如教程 10 所示）。

// 一般度规
Metric_general met (gmet) ;

// 系统
System_of_eqs syst (space, 1) ;
met.set_system (syst, "g") ;

// 可以打印未知量的数量
// 这大致对应于 6 个分量的系数数量。
cout << "Number of unknowns : " << syst.get_nbr_unknowns() << endl ;

// 传入常数
syst.add_cst ("gin", ginner) ;
syst.add_cst ("gout", gouter) ;

// 现在是方程
// 让我们使用一个“复杂”但对称的体方程
syst.add_eq_bc (1, INNER_BC, "g_ij = gin_ij") ;
syst.add_eq_inside (1, "lap(g_ij) = g_ik * R_j^k + g_jk * R_i^k") ;
syst.add_eq_bc (1, OUTER_BC, "g_ij = gout_ij") ;

// 计算初始误差
// 这确保代码正确确定了条件的数量
Array<double> errors (syst.sec_member()) ;

// 可以打印由方程产生的条件数量
cout << "Wrong number of conditions : " << syst.get_nbr_conditions() << endl ;
```

发生的情况是，代码丢失了体方程是对称的这一信息，因此它被认为是一个 9 分量的张量，从而导致了过多的条件。

### 使用 `List_comp` ###

为了解决上述问题，在定义张量方程时，需要指定要考虑哪些分量。这通过使用 `List_comp` 类显式描述分量列表来完成。

```cpp
// 带两个参数的构造器。
// 第一：要考虑的分量数量。
// 第二：阶数（即索引的数量）
List_comp used (6, 2) ; // 这里是一个二阶张量的 6 个分量。

// 手动传递分量
used.set(0)->set(0) = 1 ; used.set(0)->set(1) = 1 ; // 分量 xx
used.set(1)->set(0) = 1 ; used.set(1)->set(1) = 2 ; // 分量 xy
used.set(2)->set(0) = 1 ; used.set(2)->set(1) = 3 ; // 分量 xz
used.set(3)->set(0) = 2 ; used.set(3)->set(1) = 2 ; // 分量 yy
used.set(4)->set(0) = 2 ; used.set(4)->set(1) = 3 ; // 分量 yz
used.set(5)->set(0) = 3 ; used.set(5)->set(1) = 3 ; // 分量 zz
```

现在，在定义系统时，可以将此 `List_comp` 传递给体方程，这样它就只会考虑正确的分量。这将使条件的数量与未知量的数量保持一致。

```cpp
// 定义一个新系统 systtwo，与第一个类似，但仅使用
systtwo.add_eq_inside (1, "lap(g_ij) = g_ik * R_j^k + g_jk * R_i^k", used) ;
```

如果需要，这也可以用于其他类型的方程（匹配条件和边界条件）。

---
## 教程十二：使用文件 ##

本节教程涉及使用文件来保存和读取结果。

### 写入文件 ###

文件必须通过 `fopen` 函数打开。

对于整数和双精度浮点数，需要使用 `fwrite_be` 函数，该函数使用大端（big endian）字节序。

大多数 Kadath 类都有一个必须调用的 `save` 函数。请注意，各种场不仅需要从文件构造，还需要从 `Space` 构造，因此 `Space` 对象需要首先被保存。

```cpp
// 以写模式打开文件。
FILE* fout = fopen ("file.dat", "w") ;

// 两个待保存的值
int valint = 2 ;
double valdouble = 1.31732 ;

// 使用 fwrite_be 写入
fwrite_be (&valint, sizeof(int), 1, fout) ;
fwrite_be (&valdouble, sizeof(double), 1, fout) ;

// 假设一个 space、一个标量和一个矢量已被预先定义
// 它们通过调用 save 被保存
space.save(fout) ;
field.save(fout) ;
vecU.save(fout) ;

// 最后不要忘记关闭文件
fclose(fout) ;
```

### 读取文件 ###

显然，文件中的对象必须以它们被保存的相同顺序来读取。

对于整数和双精度浮点数，这是通过 `fread_be` 来完成的。

各种类都有从文件构造的构造函数。如上所述，这些构造函数也需要一个 `Space` 对象，因此该 `Space` 对象必须是第一个被读取的。

```cpp
// 以读模式打开文件。
FILE* fin = fopen ("file.dat", "r") ;

// 两个待读取的值
int valint  ;
double valdouble  ;

// 使用 fread_be 读取
fread_be (&valint, sizeof(int), 1, fin) ;
fread_be (&valdouble, sizeof(double), 1, fin) ;

cout << "Integer read " << valint << endl ;
cout << "Double read " << valdouble << endl ;

// 读取 Kadath 类
// 首先是 Space，其确切类型必须已知
Space_spheric space (fin) ;
cout << space << endl ;

// 然后是场
Scalar field (space, fin) ;
Vector vecU (space, fin) ;

// 最后不要忘记关闭文件
fclose(fin) ;
```