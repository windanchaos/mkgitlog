# mkgitlog
python处理git的日志
首先我在自己的github上新建里一个干净的git项目，命名为gitobject我将项目克隆到我的本地：

```
$ git clone https://github.com/windanchaos/gitobject.git
Cloning into 'gitobject'...
remote: Counting objects: 6, done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 6 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (6/6), done.
Checking connectivity... done.

```
当在一个新目录或已有目录执行 git init 时，Git 会创建一个 .git 目录。 这个目录包含了几乎所有 Git 存储和操作的对象。 如若想备份或复制一个版本库，只需把这个目录拷贝至另一处即可。该目录的结构如下所示：
```
$ ls .git/
branches        config       HEAD   index  logs     packed-refs
COMMIT_EDITMSG  description  hooks  info   objects  refs

```


该目录下可能还会包含其他文件，不过对于一个全新的 git init 版本库，这将是你看到的默认结构。 description 文件仅供 GitWeb 程序使用，我们无需关心。 config 文件包含项目特有的配置选项。 info 目录包含一个全局性排除（global exclude）文件，用以放置那些不希望被记录在 .gitignore 文件中的忽略模式（ignored patterns）。 hooks 目录包含客户端或服务端的钩子脚本（hook scripts）。

剩下的四个条目很重要：HEAD 文件、（尚待创建的）index 文件，和 objects 目录、refs 目录。 这些条目是 Git 的核心组成部分。

 1. objects 目录存储所有数据内容；
 2. refs 目录存储指向数据（分支）的提交对象的指针；
 3. HEAD 文件指示目前被检出的分支；
 4. index 文件保存暂存区信息。 


我们将详细地逐一检视这四部分，以期理解 Git 是如何运转的。

#Git的几类对象
##Git 的数据对象
Git 是一个内容寻址文件系统。核心部分是一个简单的键值对数据库（key-value data store）。 你可以向该数据库插入任意类型的内容，它会返回一个键值，通过该键值可以在任意时刻再次检索（retrieve）该内容。 可以通过底层命令 hash-object 来演示上述效果——该命令可将任意数据保存于 .git 目录，并返回相应的键值。 

```
$ cd gitobject/
$ ls .git/
branches  description  hooks  info  objects      refs
config    HEAD         index  logs  packed-refs
$ find .git/objects/
.git/objects/
.git/objects/9b
.git/objects/9b/8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
.git/objects/a4
.git/objects/a4/3b806e24202c08eb6c1c55a94956ab6deb1427
.git/objects/04
.git/objects/04/5854e387949a02251a4d6a29a028f9340020e0
.git/objects/pack
.git/objects/info

$ find .git/objects/ -type f
.git/objects/9b/8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
.git/objects/a4/3b806e24202c08eb6c1c55a94956ab6deb1427
.git/objects/04/5854e387949a02251a4d6a29a028f9340020e0
```
从根本上来讲 Git 是一个内容寻址（content-addressable）文件系统，并在此之上提供了一个版本控制系统的用户界面。.git目录下有若干文件夹，在objects中存放的是git的对象。 Git 对 objects 目录进行了初始化，并创建了 pack 和 info 子目录，但均为空。objects目录下共有3个文件。使用git log查看日志：
```
$ git log
commit 9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
Author: windanchaos <windanchaos@users.noreply.github.com>
Date:   Sat Feb 4 23:35:06 2017 +0800

    Initial commit
```
可以看到commit 9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a和
	.git/objects/9b/8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a是对应的。

现在我们可以查看 Git 是如何存储数据的。 Git 存储内容的方式——一个文件对应一条内容，以该内容加上特定头部信息一起的 SHA-1 校验和为文件命名。 校验和的前两个字符用于命名子目录，余下的 38 个字符则用作文件名。
将objects下的三个文件分别使用命令， cat-file 命令从 Git 那里取回数据。 这个命令简直就是一把剖析 Git 对象的瑞士军刀。 为 cat-file 指定 -p 选项可指示该命令自动判断内容的类型，并为我们显示格式友好的内容：
```
$ git cat-file -p 045854e387949a02251a4d6a29a028f9340020e0
100644 blob a43b806e24202c08eb6c1c55a94956ab6deb1427	README.md
$ git cat-file -p a43b806e24202c08eb6c1c55a94956ab6deb1427
# gitobjectc
$ git cat-file -p 9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
tree 045854e387949a02251a4d6a29a028f9340020e0
author windanchaos <windanchaos@users.noreply.github.com> 1486222506 +0800
committer windanchaos <windanchaos@users.noreply.github.com> 1486222506 +0800
$ cat README.md 
# gitobject
```
从以上可以得知：
1、前两个 blob分别新建了README.md文件，然后在文件中加入了“# gitobject”内容。
2、9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a记录了提交信息。



因此，可以理解为git的数据对象其实是面向单个的文件的，记录文件的变化。那么如何记录文件夹呢，下面内容就是。
##Git的树对象

先准备下：

```
echo 'rakefile txt' >rakefile
$ git hash-object -w rakefile
4b22da928d2990b0831a0c8da0ea36dd3d6c8b1a
$ mkdir lib
$ echo 'lib text' > lib/simplegit.rb
$ git hash-object -w lib/simplegit.rb
fcd8df65cbc4d6014863d5fac3206803543b116a
$ ls
lib  rakefile  README.md

```
-w 选项指示 hash-object 命令存储数据对象；若不指定此选项，则该命令仅返回对应的键值。 --stdin 选项则指示该命令从标准输入读取内容；若不指定此选项，则须在命令尾部给出待存储文件的路径。 该命令输出一个长度为 40 个字符的校验和。
```
$ find .git/objects/ -type f
.git/objects/9b/8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
.git/objects/a4/3b806e24202c08eb6c1c55a94956ab6deb1427
.git/objects/04/5854e387949a02251a4d6a29a028f9340020e0
.git/objects/fc/d8df65cbc4d6014863d5fac3206803543b116a
.git/objects/4b/22da928d2990b0831a0c8da0ea36dd3d6c8b1a
#上次的文件如下：
#.git/objects/9b/8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a
#.git/objects/a4/3b806e24202c08eb6c1c55a94956ab6deb1427
#.git/objects/04/5854e387949a02251a4d6a29a028f9340020e0
```
我把修改的内容提交到本地代码库：
```
$ git add .
$ git commit -m "add rakefile and lib "[master 4933c03] add rakefile and lib
 2 files changed, 2 insertions(+)
 create mode 100644 lib/simplegit.rb
 create mode 100644 rakefile
```
准备就绪。
接下来要探讨的对象类型是树对象（tree object），它能解决文件名保存的问题，也允许我们将多个文件组织到一起。 Git 以一种类似于 UNIX 文件系统的方式存储内容，但作了些许简化。**所有内容均以树对象和数据对象的形式存储**，其中树对象对应了 UNIX 中的目录项，数据对象则大致上对应了 inodes 或文件内容。 一个树对象包含了一条或多条树对象记录（tree entry），每条记录含有一个指向数据对象或者子树对象的 SHA-1 指针，以及相应的模式、类型、文件名信息。 例如，某项目当前对应的最新树对象可能是这样的：

```
$ git cat-file -p master^{tree}
100644 blob a43b806e24202c08eb6c1c55a94956ab6deb1427	README.md
040000 tree e74f263e7c2c38273b72e29a95f10bb7e0340f3f	lib
100644 blob 4b22da928d2990b0831a0c8da0ea36dd3d6c8b1a	rakefile

```
aster^{tree} 语法表示 master 分支上最新的提交所指向的树对象。 请注意，lib 子目录（所对应的那条树对象记录）并不是一个数据对象，而是一个指针，其指向的是另一个树对象：
```
$ git cat-file -p e74f263e7c2c38273b72e29a95f10bb7e0340f3f
100644 blob fcd8df65cbc4d6014863d5fac3206803543b116a	simplegit.rb
$ git cat-file -p fcd8df65cbc4d6014863d5fac3206803543b116a
lib text

```


从概念上讲，Git 内部存储的数据有点像这样：

![这里写图片描述](https://git-scm.com/book/en/v2/images/data-model-1.png)



你可以轻松创建自己的树对象。 通常，Git 根据某一时刻暂存区（即 index 区域，下同）所表示的状态创建并记录一个对应的树对象，如此重复便可依次记录（某个时间段内）一系列的树对象。 因此，为创建一个树对象，首先需要通过暂存一些文件来创建一个暂存区。 可以通过底层命令 update-index 为一个单独文件——我们的 readme.md 文件的首个版本——创建一个暂存区。 利用该命令，可以把 readme.md 文件的首个版本人为地加入一个新的暂存区。 必须为上述命令指定 --add 选项，因为此前该文件并不在暂存区中；同样必需的还有 --cacheinfo 选项，因为将要添加的文件位于 Git 数据库中，而不是位于当前目录下。 同时，需要指定文件模式、SHA-1 与文件名：

```

$ git update-index --add --cacheinfo 100644 \
  83baae61804e65cc73a7201a7252750c76066a30 readme.txt
```

本例中，我们指定的文件模式为 100644，表明这是一个普通文件。 其他选择包括：100755，表示一个可执行文件；120000，表示一个符号链接。 这里的文件模式参考了常见的 UNIX 文件模式，但远没那么灵活——上述三种模式即是 Git 文件（即数据对象）的所有合法模式（当然，还有其他一些模式，但用于目录项和子模块）。

现在，可以通过 write-tree 命令将暂存区内容写入一个树对象。 此处无需指定 -w 选项——如果某个树对象此前并不存在的话，当调用 write-tree 命令时，它会根据当前暂存区状态自动创建一个新的树对象：

```
$ git write-tree
d8329fc1cc938780ffdd9f94e0d364e0ea74f579
$ git cat-file -p d8329fc1cc938780ffdd9f94e0d364e0ea74f579
100644 blob 83baae61804e65cc73a7201a7252750c76066a30      readme.txt
```

不妨验证一下它确实是一个树对象：

```
$ git cat-file -t d8329fc1cc938780ffdd9f94e0d364e0ea74f579
tree
```

接着我们来创建一个新的树对象，它包括 test.txt 文件的第二个版本，以及一个新的文件：

```
$ echo 'new file' > new.txt
$ git update-index readme.txt
$ git update-index --add readme.txt
```

暂存区现在包含了 test.txt 文件的新版本，和一个新文件：new.txt。 记录下这个目录树（将当前暂存区的状态记录为一个树对象），然后观察它的结构：

```
$ git write-tree
0155eb4229851634a0f03eb265b69f5a2d56f341
$ git cat-file -p 0155eb4229851634a0f03eb265b69f5a2d56f341
100644 blob fa49b077972391ad58037050f2a75f74e3671e92      new.txt
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a      test.txt
```

我们注意到，新的树对象包含两条文件记录，同时 test.txt 的 SHA-1 值（1f7a7a）是先前值的“第二版”。 只是为了好玩：你可以将第一个树对象加入第二个树对象，使其成为新的树对象的一个子目录。 通过调用 read-tree 命令，可以把树对象读入暂存区。 本例中，可以通过对 read-tree 指定 --prefix 选项，将一个已有的树对象作为子树读入暂存区：



```
$ git read-tree --prefix=bak d8329fc1cc938780ffdd9f94e0d364e0ea74f579
$ git write-tree
3c4e9cd789d88d8d89c1073707c3585e41b0e614
$ git cat-file -p 3c4e9cd789d88d8d89c1073707c3585e41b0e614
040000 tree d8329fc1cc938780ffdd9f94e0d364e0ea74f579      bak
100644 blob fa49b077972391ad58037050f2a75f74e3671e92      new.txt
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a      test.txt
```
如果基于这个新的树对象创建一个工作目录，你会发现工作目录的根目录包含两个文件以及一个名为 bak 的子目录，该子目录包含 test.txt 文件的第一个版本。 可以认为 Git 内部存储着的用于表示上述结构的数据是这样的：
![这里写图片描述](https://git-scm.com/book/en/v2/images/data-model-2.png)

##提交对象

现在有三个树对象，分别代表了我们想要跟踪的不同项目快照。然而问题依旧：若想重用这些快照，你必须记住所有三个 SHA-1 哈希值。 并且，你也完全不知道是谁保存了这些快照，在什么时刻保存的，以及为什么保存这些快照。 而以上这些，正是提交对象（commit object）能为你保存的基本信息。


可以通过调用 commit-tree 命令创建一个提交对象，为此需要指定一个树对象的 SHA-1 值，以及该提交的父提交对象（如果有的话）。 我们从之前创建的第一个树对象开始：
```
$ echo 'first commit' | git commit-tree d8329f
fdf4fc3344e67ab068f836878b6c4951e3b15f3d
```
现在可以通过 cat-file 命令查看这个新提交对象：
```
$ git cat-file -p fdf4fc3
tree d8329fc1cc938780ffdd9f94e0d364e0ea74f579
author Scott Chacon <schacon@gmail.com> 1243040974 -0700
committer Scott Chacon <schacon@gmail.com> 1243040974 -0700

first commit
```
提交对象的格式很简单：它先指定一个顶层树对象，代表当前项目快照；然后是作者/提交者信息（依据你的 user.name 和 user.email 配置来设定，外加一个时间戳）；留空一行，最后是提交注释。

接着，我们将创建另两个提交对象，它们分别引用各自的上一个提交（作为其父提交对象）：
```
$ echo 'second commit' | git commit-tree 0155eb -p fdf4fc3
cac0cab538b970a37ea1e769cbbde608743bc96d
$ echo 'third commit'  | git commit-tree 3c4e9c -p cac0cab
1a410efbd13591db07496601ebc7a059dd55cfe9
```
这三个提交对象分别指向之前创建的三个树对象快照中的一个。 现在，如果对最后一个提交的 SHA-1 值运行 git log 命令，会出乎意料的发现，你已有一个货真价实的、可由 git log 查看的 Git 提交历史了：
```
$ git log --stat 1a410e
commit 1a410efbd13591db07496601ebc7a059dd55cfe9
Author: Scott Chacon <schacon@gmail.com>
Date:   Fri May 22 18:15:24 2009 -0700

	third commit

 bak/test.txt | 1 +
 1 file changed, 1 insertion(+)

commit cac0cab538b970a37ea1e769cbbde608743bc96d
Author: Scott Chacon <schacon@gmail.com>
Date:   Fri May 22 18:14:29 2009 -0700

	second commit

 new.txt  | 1 +
 test.txt | 2 +-
 2 files changed, 2 insertions(+), 1 deletion(-)

commit fdf4fc3344e67ab068f836878b6c4951e3b15f3d
Author: Scott Chacon <schacon@gmail.com>
Date:   Fri May 22 18:09:34 2009 -0700

    first commit

 test.txt | 1 +
 1 file changed, 1 insertion(+)
```
太神奇了： 就在刚才，你没有借助任何上层命令，仅凭几个底层操作便完成了一个 Git 提交历史的创建。 这就是每次我们运行 git add 和 git commit 命令时， Git 所做的实质工作——将被改写的文件保存为数据对象，更新暂存区，记录树对象，最后创建一个指明了顶层树对象和父提交的提交对象。 这三种主要的 Git 对象——数据对象、树对象、提交对象——最初均以单独文件的形式保存在 .git/objects 目录下。 下面列出了目前示例目录内的所有对象，辅以各自所保存内容的注释：
```
$ find .git/objects -type f
.git/objects/01/55eb4229851634a0f03eb265b69f5a2d56f341 # tree 2
.git/objects/1a/410efbd13591db07496601ebc7a059dd55cfe9 # commit 3
.git/objects/1f/7a7a472abf3dd9643fd615f6da379c4acb3e3a # test.txt v2
.git/objects/3c/4e9cd789d88d8d89c1073707c3585e41b0e614 # tree 3
.git/objects/83/baae61804e65cc73a7201a7252750c76066a30 # test.txt v1
.git/objects/ca/c0cab538b970a37ea1e769cbbde608743bc96d # commit 2
.git/objects/d6/70460b4b4aece5915caf5c68d12f560a9fe3e4 # 'test content'
.git/objects/d8/329fc1cc938780ffdd9f94e0d364e0ea74f579 # tree 1
.git/objects/fa/49b077972391ad58037050f2a75f74e3671e92 # new.txt
.git/objects/fd/f4fc3344e67ab068f836878b6c4951e3b15f3d # commit 1
```
如果跟踪所有的内部指针，将得到一个类似下面的对象关系图：
![这里写图片描述](https://git-scm.com/book/en/v2/images/data-model-3.png)


#Git 引用

我们可以借助类似于 git log 1a410e 这样的命令来浏览完整的提交历史，但为了能遍历那段历史从而找到所有相关对象，你仍须记住 1a410e 是最后一个提交。 我们需要一个文件来保存 SHA-1 值，并给文件起一个简单的名字，然后用这个名字指针来替代原始的 SHA-1 值。

在 Git 里，这样的文件被称为“引用（references，或缩写为 refs）”；你可以在 .git/refs 目录下找到这类含有 SHA-1 值的文件。 在目前的项目中，这个目录没有包含任何文件，但它包含了一个简单的目录结构：

```
$ find .git/refs/
.git/refs/
.git/refs/tags
.git/refs/heads
.git/refs/heads/master
.git/refs/remotes
.git/refs/remotes/origin
.git/refs/remotes/origin/HEAD

```
现在，你就可以在 Git 命令查看引用对应的 SHA-1 值了：
```
$ git log --pretty=oneline master
4933c032660b1b439376c37213a3bb889dadd37e add rakefile and lib
9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a Initial commit
$ git log --pretty=oneline remotes/origin/HEAD
9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a Initial commit
```
这基本就是** Git 分支的本质：一个指向某一系列提交之首的指针或引用**。 若想在第二个提交上创建一个分支，可以这么做：

$ git update-ref refs/heads/test 9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a

这个分支将只包含从第二个提交开始往前追溯的记录：
```
$ git log --pretty=oneline test
9b8d924eb8a9beaa43e8090c9d4e0a225aa4ce3a Initial commit
```

至此，我们的 Git 数据库从概念上看起来像这样：
![这里写图片描述](https://git-scm.com/book/en/v2/images/data-model-4.png)
包含分支引用的 Git 目录对象。
Figure 152. 包含分支引用的 Git 目录对象。

当运行类似于 git branch (branchname) 这样的命令时，Git 实际上会运行 update-ref 命令，取得当前所在分支最新提交对应的 SHA-1 值，并将其加入你想要创建的任何新引用中。
##HEAD 引用

现在的问题是，当你执行 git branch (branchname) 时，Git 如何知道最新提交的 SHA-1 值呢？ 答案是 HEAD 文件。

HEAD 文件是一个符号引用（symbolic reference），指向目前所在的分支。 所谓符号引用，意味着它并不像普通引用那样包含一个 SHA-1 值——它是一个指向其他引用的指针。 如果查看 HEAD 文件的内容，一般而言我们看到的类似这样：
```
$ cat .git/HEAD
ref: refs/heads/master
```
如果执行 git checkout test，Git 会像这样更新 HEAD 文件：
```
$ git checkout test
Switched to branch 'test'
$ cat .git/HEAD 
ref: refs/heads/test
```
当我们执行 git commit 时，该命令会创建一个提交对象，并用 HEAD 文件中那个引用所指向的 SHA-1 值设置其父提交字段。

你也可以手动编辑该文件，然而同样存在一个更安全的命令来完成此事：symbolic-ref。 可以借助此命令来查看 HEAD 引用对应的值：
```
$ git symbolic-ref HEAD
refs/heads/test
```
同样可以设置 HEAD 引用的值：
```
$ git symbolic-ref HEAD refs/heads/master
$ git symbolic-ref HEAD
refs/heads/master
```

不能把符号引用设置为一个不符合引用格式的值：

$ git symbolic-ref HEAD test
fatal: Refusing to point HEAD outside of refs/

##标签引用

前文我们刚讨论过 Git 的三种主要对象类型，事实上还有第四种。 标签对象（tag object）非常类似于一个提交对象——它包含一个标签创建者信息、一个日期、一段注释信息，以及一个指针。 主要的区别在于，标签对象通常指向一个提交对象，而不是一个树对象。 它像是一个永不移动的分支引用——永远指向同一个提交对象，只不过给这个提交对象加上一个更友好的名字罢了。这里就不深究了。

##远程引用

我们将看到的第三种引用类型是远程引用（remote reference）。 如果你添加了一个远程版本库并对其执行过推送操作，Git 会记录下最近一次推送操作时每一个分支所对应的值，并保存在 refs/remotes 目录下。 例如，你可以添加一个叫做 origin 的远程版本库，然后把 master 分支推送上去：

$ git remote add origin git@github.com:schacon/simplegit-progit.git
$ git push origin master
Counting objects: 11, done.
Compressing objects: 100% (5/5), done.
Writing objects: 100% (7/7), 716 bytes, done.
Total 7 (delta 2), reused 4 (delta 1)
To git@github.com:schacon/simplegit-progit.git
  a11bef0..ca82a6d  master -> master

此时，如果查看 refs/remotes/origin/master 文件，可以发现 origin 远程版本库的 master 分支所对应的 SHA-1 值，就是最近一次与服务器通信时本地 master 分支所对应的 SHA-1 值：

$ cat .git/refs/remotes/origin/master
ca82a6dff817ec66f44342007202690a93763949

远程引用和分支（位于 refs/heads 目录下的引用）之间最主要的区别在于，远程引用是只读的。 虽然可以 git checkout 到某个远程引用，但是 Git 并不会将 HEAD 引用指向该远程引用。因此，你永远不能通过 commit 命令来更新远程引用。 Git 将这些远程引用作为记录远程服务器上各分支最后已知位置状态的书签来管理。

本文内容及截图节选自：https://git-scm.com/book/zh/v2
