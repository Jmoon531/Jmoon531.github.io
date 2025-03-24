---

Created at: 2021-08-16
Last updated at: 2021-08-16
Source URL: about:blank


---

# 7-ArrayList源码笔记


ArrayList底层是数组，如果使用无参构造器，则初始化容量是0，在第一次添加时会扩容到10，以后每次扩容都是扩到原来的1.5，比如10会扩容到15；如果使用指定大小的有参构造器，则初始化时就是这个容量，以后每次扩容也是扩到原来的1.5。

常量和字段：
```
// 默认容量，10
private static final int DEFAULT_CAPACITY = 10;
private static final Object[] EMPTY_ELEMENTDATA = {};
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
// 存元素的数组
transient Object[] elementData; // non-private to simplify nested class access
// 数组中元素的个数
private int size;
```

构造器
```
// 带初始容量的构造器
public ArrayList(int initialCapacity) {
    //初始容量大于0，直接初始化，不延迟创建
    if (initialCapacity > 0) {
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;
    } else {
        throw new IllegalArgumentException("Illegal Capacity: "+
                                           initialCapacity);
    }
}

// 无参构造器
public ArrayList() {
    //先赋空数组，等到添加的时候再扩容到默认容量
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

add()方法：
```
public boolean add(E e) {
    modCount++;
    add(e, elementData, size);
    return true;
}

private void add(E e, Object[] elementData, int s) {
    // 如果数组中元素的个数等于数组的长度就扩容
    if (s == elementData.length)
        //扩容
        elementData = grow();
    //扩容后赋值
    elementData[s] = e;
    //个数加1
    size = s + 1;
}
```

扩容方法：
```
private Object[] grow() {
    return grow(size + 1);
}

//minCapacity是实际需要的最小容量
private Object[] grow(int minCapacity) {
    //旧容量
    int oldCapacity = elementData.length;
    //旧容量大于0，需要在创建数组并复制元素
    if (oldCapacity > 0 || elementData != DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        //计算新容量，主要是oldCapacity >> 1，这个表示原容量的0.5倍，newCapacity = oldCapacity + oldCapacity >> 1
        int newCapacity = ArraysSupport.newLength(oldCapacity,
                minCapacity - oldCapacity,  /* minimum growth */
                oldCapacity >> 1            /* preferred growth */ );
        //创建新数组并复制元素
        return elementData = Arrays.copyOf(elementData, newCapacity);
    } else {//旧容量等于0表示使用无参构造器后第一此添加元素，可以直接创建数组，不需要复制
        //实际需要的最小容量 和 默认容量中 选大的那个，哪肯定是默认容量大呀
        return elementData = new Object[Math.max(DEFAULT_CAPACITY, minCapacity)];
    }
}
```

