---

Created at: 2021-08-16
Last updated at: 2021-08-19
Source URL: about:blank


---

# 8-HashMap源码笔记


HashMap的数据结构是：数组+链表+红黑树。数组的每一个位置称为bin(桶)。

HashMap的put元素的流程：
首先根据key的hash值找到在数组中应该插入的位置，然后先判断这个位置是否为空，若为空就直接插在数组的这个位置，否则就依次检查链表上的每一个节点，判断key值是否相等，若相等，就替换value值，若没一个相等的，就插到链表尾部，插入后如果链表长度大于8，则还需要把链表变成红黑树。插完之后最后还要检查节点总数是否大于阈值，如果大于还需进行扩容。
注意：检查头节点和检查链表后面的节点并不是在一起的操作

HashMap的扩容机制：
`当数组长度小于64时`，若节点总数大于阈值（数组长度\*负载因子），或某个链表的长度大于树化的阈值，出现这两种情况中的任意一种情况就会将数组扩容为原来的两倍；`当数组长度大于64时`，只会在节点总数大于阈值时扩容，若某个链表的长度等于树化的阈值，则会将链表变成红黑树。
注意两点：1.是节点总数与数组长度\*负载因子比较，而不是数组上已被占有的位置  2. 数组长度小于64时，链表长度等于8不会触发树化，而是触发扩容

看注释，解读都在注释里。

常量的含义：
```
//默认数组的初始容量为16
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // aka 16
//数组的最大长度
static final int MAXIMUM_CAPACITY = 1 << 30;
//默认的负载因子
static final float DEFAULT_LOAD_FACTOR = 0.75f;
//树化的阈值，即当满足树化的条件（数组长度大于64），若链表的长度为8则树化
static final int TREEIFY_THRESHOLD = 8;
//解除树化的阈值，扩容之后需要重新将已经树化的每个元素映射到新的桶位上，此时若新桶位上的节点树小于6，这不会继续维持红黑树的结构
static final int UNTREEIFY_THRESHOLD = 6;
//树化需要满足数组长度最小为64
static final int MIN_TREEIFY_CAPACITY = 64;
```

字段：
```
//数组
transient Node<K,V>[] table;
//方法keySet() 和 values()的返回结果，不重要
transient Set<Map.Entry<K,V>> entrySet;
//节点总数
transient int size;
//修改次数，不重要
transient int modCount;
//扩容阈值
int threshold;
//负载因子
final float loadFactor;
```

构造器
```
/**
* 最主要的一个构造器，其它构造器都是调用它，可以看到构造器并没有创建数组，只是给threshold和loadFactor赋值，这是因为想延迟创建
*/
public HashMap(int initialCapacity, float loadFactor) {
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal initial capacity: " +
                initialCapacity);
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal load factor: " +
                loadFactor);
    this.loadFactor = loadFactor;
    // tableSizeFor(initialCapacity)会返回大于等于initialCapacity的最小2的幂次，然后赋给threshold
    // 为什么要赋给threshold呢？因为HashMap的数组被设计成延迟创建，先赋给threshold，等到添加一个元素时再调用resize()方法扩容，
    // 到那时才会创建数组，数组长度也就是threshold，然后再给threshold赋新值即数组长度*负载因子
    this.threshold = tableSizeFor(initialCapacity);
}

/**
* 一个参数的构造器调用两个参数的构造器，使用默认的负载因子0.75
*/
public HashMap(int initialCapacity) {
    this(initialCapacity, DEFAULT_LOAD_FACTOR);
}

/**
* 最常使用的无参构造器，使用默认的负载因子0.75，
* 其它字段就直接是对象初始化时的默认值，如 table=null threshold=0
*/
public HashMap() {
    this.loadFactor = DEFAULT_LOAD_FACTOR; // all other fields defaulted
}
```

put()方法
```
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

/**
* put()方法的核心是这个方法
*/
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    //一些临时变量，n是数组长度，i是元素应该插入的桶的位置
    HashMap.Node<K,V>[] tab; HashMap.Node<K,V> p; int n, i;
    //先将table赋给临时变量tab，然后再判断是否为空，后面还会有很多这样 赋值并判断写在一起 的骚操作，
    // 这个if语句就是检查数组是否为空或长度为0
    if ((tab = table) == null || (n = tab.length) == 0)
        // 扩容并赋值，写在一起的骚操作
        n = (tab = `resize()`).length;
    // 已经创建过数组了，i = (n - 1) & hash 找到元素应该插入的位置，然后看数组的这个位置是否为空，p这时指向了头元素
    if ((p = tab[i = (n - 1) & hash]) == null)
        // 为空就直接放在这里
        tab[i] = newNode(hash, key, value, null);
    // 已经创建过数组了，但是头节点不为空，就需要继续判断了
    else {
        HashMap.Node<K,V> e; K k;
        // p.hash == hash 与头节点的hash值相同，并且 (k = p.key) == key 与头节点的key指向的是同一个元素 或者
        // 虽然与头节点的key指向的不是同一个元素，但是(key != null && key.equals(k)) 与头节点的值相同，
        // 那么赋值给e，然后到最后一个if，判断是否替代节点的value值
        if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        // 如果与头节点的Key不相同，就需要往下走了，这里判断是否已经树了，如果树化了，就按树化的逻辑插入或者替换
        else if (p instanceof HashMap.TreeNode)
            e = ((HashMap.TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        // 按链表的逻辑走
        else {
            //遍历头节点后面的每一个元素
            for (int binCount = 0; ; ++binCount) {
                //走到尾了，直接插入
                if ((e = p.next) == null) {
                    //直接插入
                    p.next = newNode(hash, key, value, null);
                    // 如果已经遍历7个元素了，加上最后创建的这个也就是链表上不包括头节点有8个节点了，
                    // 这时需要树化，treeifyBin(tab, hash);方法首先会判断数组的长度是否小于64，
                    // 小于直接扩容，大于才树化。
                    if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                        treeifyBin(tab, hash);
                    break;
                }
                //还没走到末尾，发现有key相同的，那么break出去，后面的if会判断是否替换value
                if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        // 替换value值
        if (e != null) { // existing mapping for key
            V oldValue = e.value;
            // onlyIfAbsent表示只有缺少才做替换，调用put就是false，也就是，替换value
            // 这个调用putIfAbsent()方法才有用
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e);
            return oldValue;
        }
    }
    ++modCount;
    //size加1，如果超过阈值就扩容
    if (++size > threshold)
        `resize();`
    afterNodeInsertion(evict);
    return null;
}

// 该方法首先会判断数组的长度是否小于64，小于直接扩容，大于才树化。
final void treeifyBin(Node<K,V>[] tab, int hash) {
    int n, index; Node<K,V> e;
    if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
        `resize()`;
    else if ((e = tab[index = (n - 1) & hash]) != null) {
        TreeNode<K,V> hd = null, tl = null;
        do {
            TreeNode<K,V> p = replacementTreeNode(e, null);
            if (tl == null)
                hd = p;
            else {
                p.prev = tl;
                tl.next = p;
            }
            tl = p;
        } while ((e = e.next) != null);
        if ((tab[index] = hd) != null)
            hd.treeify(tab);
    }
}
```

扩容方法
```
/**
* 扩容方法
*/
final HashMap.Node<K,V>[] resize() {
    HashMap.Node<K,V>[] oldTab = table;
    // 旧容量
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    // 旧阈值
    int oldThr = threshold;
    // 新容量，新阈值，下面十几行都是在确定它俩的值
    int newCap, newThr = 0;
    // 旧容量大于0，数组不为空，表示这是一次`常规的扩容操作`
    if (oldCap > 0) {
        // 如果旧容量大于最大容量，一般很少出现
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        // 先把旧容量的两倍赋给新容量
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                // 如果旧容量小于16
                oldCap >= DEFAULT_INITIAL_CAPACITY)
            // 如果旧容量小于16，不会把旧的阈值赋给新阈值（情况一，下面的if语句再会给newThr赋值），
            // 不小于直接把旧阈值的两倍赋给新阈值
            newThr = oldThr << 1; // double threshold
    }
    // 走到这表示旧容量为0，旧阈值大于0，只有调用有参构造，在第一次往map中添加元素才会出现这种情况
    else if (oldThr > 0) // initial capacity was placed in threshold
        //旧阈值赋给新容量（情况二，下面的if语句再会给newThr赋值）
        newCap = oldThr;
    // 走到这表示旧容量为0，旧阈值也为0，只有调用无参构造，在第一次往map中添加元素才会出现这种情况
    else {               // zero initial threshold signifies using defaults
        //新容量等于16，新阈值等于12
        newCap = DEFAULT_INITIAL_CAPACITY;
        newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
    }
    //新阈值等于0，给上面的两种情况的newThr赋值
    if (newThr == 0) {
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                (int)ft : Integer.MAX_VALUE);
    }
    //新阈值赋给成员变量
    threshold = newThr;
    //至此，新容量和新阈值旧确定完成了

    //扩容操作开始
    @SuppressWarnings({"rawtypes","unchecked"})
    //扩容
    HashMap.Node<K,V>[] newTab = (HashMap.Node<K,V>[])new HashMap.Node[newCap];
    table = newTab;
    //不是第一次扩容
    if (oldTab != null) {
        //遍历数组的每一个元素
        for (int j = 0; j < oldCap; ++j) {
            HashMap.Node<K,V> e;
            //如果数组元素不为空
            if ((e = oldTab[j]) != null) {
                //旧数组元素置空是为了方便GC
                oldTab[j] = null;
                //如果没有下一个元素，也就是只有头节点
                if (e.next == null)
                    //直接把这个元素放到新数组中
                    newTab[e.hash & (newCap - 1)] = e;
                // 否则，如果是树，把树的每个节点重新散列到新数组中
                else if (e instanceof HashMap.TreeNode)
                    ((HashMap.TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                // 否则，则是链表，把链表的每个节点重新散列到新数组中
                else { // preserve order
                    //这里涉及到一个算法，就是按倍数扩容之后，重新散列只有两种情况，一是散列到新数组相同的位置上，
                    // 二是散列到新数组的位置=原来的位置+原来的容量，因为位置是这样计算的 hash & (n-1)，n是数组容量，
                    // 两次结果低位是相同的，只有新增加的高位不同，0或者是1
                    HashMap.Node<K,V> loHead = null, loTail = null;
                    HashMap.Node<K,V> hiHead = null, hiTail = null;
                    HashMap.Node<K,V> next;
                    do {
                        next = e.next;
                        //高位是0的链起来
                        if ((e.hash & oldCap) == 0) {
                            if (loTail == null)
                                loHead = e;
                            else
                                loTail.next = e;
                            loTail = e;
                        }
                        //高位是1的链起来
                        else {
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);
                    //放到新数组中
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;
                    }
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;
                    }
                }
            }
        }
    }
    return newTab;
}
```

