maven两大作用：1.自动构建项目 2.依赖管理

```xml
<!-- settings.xml 下的配置 -->
    本地仓库的位置：
    <localRepository>/path/to/local/repo</localRepository>

    更换阿里云镜像：
    <mirror>
        <id>aliyunmaven</id>
        <mirrorOf>*</mirrorOf>
        <name>阿里云公共仓库</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
```

- mvn dependency:tree 打印项目的整个依赖树
- mvn archetype:generate 根据原型（模板）创建Maven项目
  比如根据Maven Simple Project Archetype创建普通的java项目：
  mvn archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DarchetypeArtifactId=maven-archetype-simple -DarchetypeVersion=1.4

- mvn tomcat7:run 在tomcat容器中运行web应用  mvn jetty:run 在jetty容器中运行web应用


- 命令参数

  -D传入属性参数
  mvn package -Dmaven.test.skip=true 打包时跳过单元测试，idea右侧的⚡图标就是这个功能

  -P使用指定的profile配置

- 运行mvn工程
  mvn exec:java -Dexec.mainClass="com.xxx.demo.Hello"

- 继承

  1. 继承必须在子模块中用<parent>指明父模块（maven术语：继承）

  - 继承时，会继承groupId和version，如果子模块指定了groupId和version，则会覆盖父模块的，以子模块为准；还会继承父模块的依赖，**继承最主要的就是这个作用，统一管理子模块都用到了的依赖**。

  2. 在父模块中用<moudle>指明子模块，指明子模块后可以在父模块的pom.xml下运行一键安装（maven术语：聚合）

  3. 具有继承关系的模块，在maven工程的目录结构上也最好具有同样的层次关系，不然的话需要在子模块pom.xml中的<parent>下配置<relativePath>指明父模块的相对路径，才能正确继承，因为**<relativePath>的默认值是../pom.xml**（也就是说maven默认也想你用这样层级结构的目录来建立工程）；也需要在<moudle>正确地指明较为复杂的相对路径，才能在父模块下正确地运行一键安装。

  - 不过，在子模块pom.xml中的<parent>下配置<relativePath>还有一个作用就是，即使没有安装父模块，也能安装子模块并且正确地继承父模块。
  - 也就是如果指明了<relativePath>，那就去该路径下去找父模块；如果没有配置<relativePath>，那就先去上一级目录找父模块（这是默认值），上一级没有maven工程那就去仓库里找，仓库里没有就build failure.

  4. 在目录上保持这种层次关系可以十分清晰的说明这个工程的结构，而且父模块可以说只有pom.xml文件有用，因为被继承的模块（父模块）的打包方式是pom，在这种打包方式下，即使父模块有主程序代码，也不会生成jar，我们不应该让一个maven工程的目录只有pom.xml孤零零的放在那，再说既然具有继承关系，也就是一个工程，所以更应该把子模块目录放在父模块目录中，保持这种继承的目录层次结构。不过，安装时以模块声明的**坐标**为准安装在仓库中，与maven工程的目录结构没有关系。

  - idea管理maven模块的继承关系，不仅需要在子模块中配置<parent>，也要在父模块中配置<moudle>，所以在idea中，只要正确的配置了<moudle>，子模块和父模块的目录可以不具有层次关系，但是这无疑是给自己找麻烦，所以最好顺从这种目录结构，约定大于配置。不要在<parent>下配置<relativePath>，因为咱们已经严格按照继承的目录结构建立了工程，而<relativePath>的默认值就是../pom.xml，这是正确的，所以可以单独安装子模块，并且已经配置了<moudle>，也可以在父模块进行一键安装。

- 依赖传递的原则：1.路径最短者优先  2.路径相同先声明者优先

- **继承**可以只install子模块，不安装父模块（前提是在子模块pom.xml中的<parent>下正确配置<relativePath>），但是对于**依赖**，不管是编译（这里的编译是指maven default生命周期的阶段，与idea中的编译运行不同，idea的编译运行能正确找到配置的依赖）还是安装，都必须先安装被依赖的模块。

- 可运行的jar（在META-INF/MANIFEST.MF中指明main-class，也就指明了程序的入口）就是插件，其他的jar就是类库，即常说的jar包。

- maven的生命周期就是调用相应的maven**插件**执行任务，为了代码复用，相似的任务用同一插件完成，因为他们的做的事大部分都相同，具体的差异用不同的**目标**区分，比如编译的任务用maven-compiler-plugin:3.1插件完成，但是对待主程序和测试程序的编译有些许差异，于是用不同的目标区分，即编译主程序的目标是compile，编译测试程序的目标是testCompile，可以理解成同一个函数，传不同的参数。

- 可以在maven仓库中安装其他插件，如果maven工程需要用到非maven的插件，比如jetty和tomcat的插件，需要在下面的标签中定义；也可以定义maven插件用于指定版本，也只是为了指定版本，因为即使没有指定maven插件，在构建工程时也会调用默认的maven插件。

```xml
<build>
    <pluginManagement>
        <plugins>
            
            <plugin>
          		<groupId>org.eclipse.jetty</groupId>
          		<artifactId>jetty-maven-plugin</artifactId>
          		<version>9.4.15.v20190215</version>
				<configuration>
                    <scanIntervalSeconds>10</scanIntervalSeconds>
                    <webApp>
                        <contextPath>/webapp</contextPath>
                    </webApp>
          		</configuration>
        	</plugin>
            
        </plugins>
    </pluginManagement>
</build>
```

- 使用 maven jetty plugin 部署一个多模块的web项目的步骤：
  ① 必须先安装其它被依赖的模块
  ② 然后在web模块的pom.xml目录下运行jetty插件 mvn jetty:run (运行jetty的web模块不必 安装 或者 打包 或者 编译，因为jetty插件的run目标会完成 编译 和 部署)
  所以使用maven插件来部署项目十分的麻烦，因为如果被依赖的模块有改动，必须自己手动重新安装被依赖的模块才能生效。

  如果不对项目划分多个模块，dao层、service层和controller层放在同一个模块的不同包中，那么用maven插件来部署项目会很方便，但我用maven不就是冲着它可以划分模块，在模块之间进行依赖管理来的吗，好吧，综上，使用maven来管理项目，但不要使用maven插件来部署项目，使用idea集成外部独立的服务器来部署项目更好，idea会分析模块之间的依赖，然后合理的编译各个模块并部署web模块。

- 父工程使用dependencyManagement不实际导入依赖，子工程需要显示的声明依赖，故而dependencyManagement主要用于管理版本。


------

------



- 最佳实践是把conf/settings.xml文件复制一份到 [用户目录]/.m2/ 下，以后只修改这个settings.xml文件的内容，因为idea默认是读取这个配置文件的内容，这样下载的maven和idea都是读取这个配置文件了。
- 解决 *不再支持源选项 5。请使用 7 或更高版本。*错误

```xml
<properties>
    <maven.compiler.source>15</maven.compiler.source>
    <maven.compiler.target>15</maven.compiler.target>
</properties>
```

- 打成带主类的jar包

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>3.0.2</version>
            <configuration>
                <archive>
                    <manifest>
                        <addClasspath>true</addClasspath>
                        <mainClass>fully.qualified.MainClass</mainClass>
                    </manifest>
                </archive>
            </configuration>
        </plugin>
    </plugins>
</build>
```

- idea 右侧的文件夹刷新图标的功能是执行了maven资源插件的两个目标  maven-resources-plugin:resources和maven-resources-plugin:testResources

  