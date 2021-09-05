# QML与C++交互

## 前言

### 参考

[QML与C++数据绑定](https://www.jianshu.com/p/b1a99066f647)

[Qt Quick 之 QML 与 C++ 混合编程详解](https://blog.csdn.net/foruok/article/details/32698603)

[QML与C++集成<一>——<运行环境以及相关运行时类介绍>](https://www.cnblogs.com/laiyingpeng/p/12335608.html)

[QML与C++集成<二>——<使用C++属性及注册QML类型>](https://www.cnblogs.com/laiyingpeng/p/12336848.html)

[QML与C++交互](https://blog.csdn.net/gongjianbo1992/article/details/87965925)

[C++注册QML](https://blog.csdn.net/weixin_42353082/article/details/97135511)

[QQmlEngine Class](https://doc.qt.io/qt-5/qqmlengine.html#qmlRegisterType)

[QQmlContext Class](https://doc.qt.io/qt-5/qqmlcontext.html#setContextProperty)

以下内容大部分为摘抄。

### QML运行环境加载

QML应用程序通常有以下两种加载`QQmlEngine`：

1. 通过`QQuickView`搭配`Item`加载QML文件
2. 创建一个`QQmlApplicationEngine`，并搭配Window加载QML文件

## QML调用C++

### 背景

QML其实是对JavaScript的扩展，融合了Qt Object系统，它是一种新的解释型的语言， QML引擎虽然由Qt C++ 实现，但QML对象的运行环境，说到底和C++对象的上下文环境是不同的，是平行的两个世界。

因为QML引擎与Qt的元对象系统的集成，使得在QML中可以直接调用C++的功能，这种机制还允许QML、JavaScript、C++三者进行混合开发。在QML引擎中集成了Qt元对象系统，所以QObject子类能够将数据或函数提供给QML使用，由QObject派生的所有子类的属性、方法和信号等都可以在QML中访问。

Qt提供了两种在QML环境中使用C++对象的方式：

1. **注册类型(qmlRegisterType)**，**C++类可以注册为一个可以_实例化_QML类型,**这样就可以像其他普通QML对象类型一样在QML代码中被实例化使用。
2. **使用属性(setContextProperty)**，**C++类的实例可以作为上下文属性或上下文对象嵌入到QML代码中。**

其两者都是将C++类暴露给QML的方法，但不管哪种方式，对要导出的 C++ 类都有要求，不是一个类的所有方法、变量都可以被 QML 使用。

### 注册属性 qmlRegisterType

注册QML类型，有多种方法可用，如 `qmlRegisterSingletonType()` 用来注册一个单例类型， `qmlRegisterType()`注册一个非单例的类型， `qmlRegisterTypeNotAvailable()` 注册一个类型用来占位， `qmlRegisterUncreatableType()` 通常用来注册一个具有附加属性的附加类型。

常规使用的是`qmlRegisterType`。

This template function registers the C++ type in the QML system with the name *qmlName*, in the library imported from *uri* having the version number composed from *versionMajor* and *versionMinor*.

```c++
template<typename T>

int qmlRegisterType(const char *uri, int versionMajor, int versionMinor, const char *qmlName);
//uri 指定一个唯一的包名 
//versionMajor versionMinor 主次版本
//qmlName QML 中可以使用的类名

template<typename T, int metaObjectRevision>

int qmlRegisterType(const char *uri, int versionMajor, int versionMinor, const char *qmlName);
```

#### 注册可实例化对象类型

**注册可实例化的类**意味着这个类定义为一个QML对象类型，QML对象类型通过这种注册能够获取这种类型的元数据，以及相关属性信号等操作。

```c++
//注册 MySliderItem 类到QML中
qmlRegisterType<MySliderItem>("com.mycompany.qmlcomponents", 1, 0, "Slider");

//注册后就可以在QML中导入
import com.mycompany.qmlcomponents 1.0

//在QML中实例化
Slider {
    id: slider
    // ...
}
```

#### 注册不可实例化对象类型

注册不可实例化的C++类，意味着这种类型不可实例化，比如要把_枚举类型_暴露给QML，但这个类型本身不需要被实例化。

有以下特征：是接口类型；一个基类，不需要通过QML代码访问；仅仅提供一些有用的枚举；是一个单例，只能使用其唯一的实例，不应该从QML进行实例化。

**枚举注册QML**

```c++
class TypeState : public QObject //继承自QObject
{
    Q_OBJECT
public:
    enum Status {
        E1 = 1,           
        E2,            
        E3,            
        E4,                   
    };
    Q_ENUMS(Status)
};

//注册到QML
qmlRegisterType<TypeState>("EnumType", 1, 0, "eenum");
```

### 注册类型 setContextProperty

```c++
void QQmlContext::setContextProperty(const QString &name, QObject *value)
//Set the value of the name property on this context.    
```

```c++
//注册 MySliderItem 到QML中：
int main(int argc, char *argv[])
{
	QQmlApplicationEngine engine;
	//实例化一个类 
    MySliderItem myslideritem;
    //"myslideritem" 小写字母开头，QML才能访问C++对象的函数与属性
    ////注册到上下文
    engine.rootContext()->setContextProperty("myslider", &myslideritem);
}
//从堆上分配了一个 myslideritem 对象，然后注册为 QML 上下文的属性，起了个名字就叫 myslider,setContextProperty() 方法可以为该上下文设置一个全局可见的属性。

//QML中使用
不用import 直接使用 myslider.属性(可访问的)
```

**使用注册属性的几种情况**

* 比如我们有一个功能单一的Configure类，我们需要把它暴露给QML，在使用之前必须要先创建类对象m_configuration，就是说类实例化一次，QML中可以直接使用这个类，注意功能单一的类只适合该方式；
* 比如我们的业务比较复杂，我们有很多类，若要供QML调用，我们就要写一个总的被调用类Complex（包含所有的业务类），然后实例化一次这个Complex,然后QML中直接使用实例化后的对象；

### QML中可以访问的C++属性

导出了一个C++类，在 QML 中就必然要访问该类的实例的属性或方法来达到某种目的，以下特征的属性或方法才可以被 QML 访问。

#### 前提条件

要想将一个类或对象导出到QML中，必须满足：

* **从QObjetct或QObject的派生类继承**
* **使用Q_OBJECT宏**

这两个条件是为了让一个类能够进入 Qt 强大的元对象系统（meta-object system）中，只有使用元对象系统，一个类的某些方法或属性才可能通过字符串形式的名字来调用，才具有了在 QML 中访问的基础条件。

#### 信号和槽

*只要是信号或者槽，都可以在 QML 中访问。*

1. 可以把 C++ 对象的信号连接到 QML 中定义的方法上

2. 也可以把 QML 对象的信号连接到 C++ 对象的槽上

3. 还可以直接调用 C++ 对象的槽或信号

```c++
class ColorMaker : public QObject
{
    Q_OBJECT
 
public:
    ColorMaker(QObject *parent = 0);
    ~ColorMaker();
//使用 signals 标记信号函数，信号是一个函数声明，返回 void，不需要实现函数代码； 
signals:
    void colorChanged(const QColor & color);
    void currentTime(const QString &strTime);
//槽函数是普通的成员函数，作为成员函数，会受到 public、private、protected 的影响； 
public slots:
    void start(const QString& startNum);
    void stop();   
};
```

##### 槽(public slots)

`ColorMaker`注册后直接在qml中调用槽。

```c++
colormaker.start("123");
colormaker.stop();
```

##### 信号(signals)

QML代码可以使用QObject子类的任意public信号，_QML引擎会为每一个来自QObject子类的信号自动创建一个信号处理器_，其命名规则如为：`on<Signal>`，其中`<Signal>`为信号的名字，首字母要大写，信号传递的参数通过其名字在信号处理器中使用。

**C++信号连接QML槽**

```javascript
//C++ .h
signals:
    void colorChanged(const QColor & color);
    void currentTime(const QString &strTime);
    
//.c 发送信号
//要避免递归
emit currentTime("2021.9.5");

//qml 槽函数
function logCurrentTime(str)
{
	console.log("currentTime is " + str)
}

//C++信号连接QML槽函数
Component.onCompleted: {
	colormaker.currentTime.connetc(logCurrentTime)
}
```

#### Q_INVOKABLE 宏

在定义一个类的成员函数时使用 Q_INVOKABLE 宏来修饰，就可以让该方法被元对象系统调用。_这个宏必须放在返回类型前面_。

`Q_INVOKABLE GenerateAlgorithm algorithm() const;
 Q_INVOKABLE void setAlgorithm(GenerateAlgorithm algorithm);`

```c++
class ColorMaker : public QObject
{
    Q_OBJECT	
    Q_ENUMS(GenerateAlgorithm)
        
public:
    ColorMaker(QObject *parent = 0);
    ~ColorMaker();
    
    enum GenerateAlgorithm{
        RandomRGB,
        RandomRed,
        RandomGreen,
        RandomBlue,
        LinearIncrease
    };
    
    Q_INVOKABLE GenerateAlgorithm algorithm() const;
    Q_INVOKABLE void setAlgorithm(GenerateAlgorithm algorithm);
 
signals:
    void colorChanged(const QColor & color);
    void currentTime(const QString &strTime);
 
public slots:
    void start();
    void stop();
};
```

注册`ColorMaker`类后，在 QML 中就可以用 ${Object}.${method} 来访问。

```javascript
Component.onCompleted: {
        colorMaker.setAlgorithm(ColorMaker.LinearIncrease);
    }
```

#### Q_ENUMS枚举

要导出的类定义了想在 QML 中使用枚举类型，可以使用 Q_ENUMS 宏将该枚举注册到元对象系统中。

使用 Q_ENUMS 宏注册了你的枚举类型，在 QML 中就可以用 ${CLASS_NAME}.${ENUM_VALUE} 的形式来访问。

```javascript
   Component.onCompleted: {
        colorMaker.color = Qt.rgba(0,180,120, 255);
        colorMaker.setAlgorithm(ColorMaker.LinearIncrease);
        changeAlgorithm(colorAlgorithm, colorMaker.algorithm());
    }
//ColorMaker.LinearIncrease 
```

#### Q_PROPERTY

 Q_PROPERTY 宏用来定义可通过元对象系统访问的属性，通过它定义的属性，可以在 QML 中访问、修改，也可以在属性变化时发射特定的信号。

```c++
Q_PROPERTY(type name
           (READ getFunction [WRITE setFunction] |
            MEMBER memberName [(READ getFunction | WRITE setFunction)])
           [RESET resetFunction]
           [NOTIFY notifySignal]
           [REVISION int]
           [DESIGNABLE bool]
           [SCRIPTABLE bool]
           [STORED bool]
           [USER bool]
           [CONSTANT]
           [FINAL])
```

```c++
/*name.h*/
#include <QObject>

class Name : public QObject //继承自QObject
{
    Q_OBJECT//QObject宏
    Q_PROPERTY(QString data READ data WRITE setData NOTIFY dataChanged)
public:
    Name(QObject *parent = nullptr);//默认构造函数
    Name(QString _name);//构造函数

    QString data() const;//READ 接口
    void setData(const QString& _data);//WRITE 接口

signals:
    QString dataChanged();//NOTIFY 信号（不需实现）

private:
    QString m_data;//私有属性
};
```

_Warning：不要在 cpp 文件中直接定义类，因为 Q_OBJECT 宏需要经过 moc 处理，非 `.h` 文件不会被 moc 处理，编译时出现“无法识别的符号”错误。_

`Q_PROPERTY(QString data READ data WRITE setData NOTIFY dataChanged)`

提供的对象是一个 QString，READ 接口是一个名为 data 的函数， WRITE 接口是一个名为 setData 的函数，NOTIFY 接口用于通知的绑定，只有设置了 NOTIFY 接口，QML 才能自动与 C++ 中的属性同步。

```c++
/*name.cpp*/
#include "name.h"

Name::Name(QObject *parent) : QObject(parent)
{//默认构造函数
}

Name::Name(QString _data) : m_data(_data)
{//自定义构造函数，初始化私有对象m_data
}

QString Name::data() const
{
    return m_data;//READ 接口实现，返回私有对象
}

void Name::setData(const QString& _data)
{
    if(_data != m_data){//WRITE 接口实现，更新m_data并发出信号
        m_data = _data;
        emit dataChanged();
    }
}
```

**注册到上下文**

实例化一个 Name 类并注册到上下文。注册需要在读取`.qml`文件之前完成。

```c++
/*main.cpp*/
Name a_name("test");

QQmlApplicationEngine engine;
QQmlContext* rootContex = engine.rootContext();//拿到engine的根上下文
rootContex->setContextProperty("name",  QVariant::fromValue(a_name));//注册
engine.load(QUrl(QStringLiteral("qrc:/main.qml")));
```

**在QML中读取**

QML 中可以读取到接口返回的属性，直接给属性赋值，并且监听到属性变化。

```javascript
/*main.qml*/
Rectangle {
    Text {
        text:name.data //相当于调用name.data()这个接口

        Connections {//建立一个到NOTIFY接口的连接
            target: name
            onDataChanged:{//对应NOTIFY接口
                console.log("data has beed changed!");
            }
        }
    }

    Button {
        text:"changeData"
        onClicked: {
            name.data = "hasChanged!";
        }
    }
}
```

Connections 用来监听事件，监听的 target 是定义了 NOTIFY 的对象（注意 onDataChanged 这个 event handler 的驼峰命名法和原 NOTIFY 定义时的命名。也就是前面信号所说的，_QML引擎会为每一个来自QObject子类的信号自动创建一个信号处理器_，其命名规则如为：`on<Signal>`，其中`<Signal>`为信号的名字，首字母要大写，信号传递的参数通过其名字在信号处理器中使用。

