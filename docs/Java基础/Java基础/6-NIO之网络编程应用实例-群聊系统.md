---

Created at: 2021-08-15
Last updated at: 2021-11-10


---

# 6-NIO之网络编程应用实例-群聊系统


群聊系统：客户端先把消息发送到服务器，然后由服务器发送给除发送消息的客户端之外的所有客户端
服务器端
```
public class Server {
    public static void main(String[] args) throws IOException {
        List<SocketChannel> channels = new ArrayList<>();
        Selector selector = Selector.open();
        ByteBuffer buf = ByteBuffer.allocate(1024);
        ServerSocketChannel ssChannel = ServerSocketChannel.open();
        ssChannel.configureBlocking(false);
        ssChannel.bind(new InetSocketAddress(9999));
        ssChannel.register(selector, SelectionKey.OP_ACCEPT);
        while (selector.select() > 0) {
            Iterator<SelectionKey> it = selector.selectedKeys().iterator();
            while (it.hasNext()) {
                SelectionKey sk = it.next();
                if (sk.isAcceptable()) {
                    SocketChannel sChannel = ssChannel.accept();
                    channels.add(sChannel);
                    sChannel.configureBlocking(false);
                    sChannel.register(selector, SelectionKey.OP_READ);
                } else if (sk.isReadable()) {
                    SocketChannel sChannel = (SocketChannel) sk.channel();
                    try {
                        // socket异常关闭时，会发送一个异常的消息给服务器，是个可读事件，
                        // 但是具体又读不出东西来，因而抛异常
                        while ((sChannel.read(buf)) > 0) {
                            // 发送给除自己之外的所有客户端
                            for (SocketChannel socketChannel : channels) {
                                if (socketChannel != sChannel) {
                                    buf.flip();
                                    socketChannel.write(buf);
                                }
                            }
                            buf.clear();
                        }

                    } catch (SocketException e) {
                        // 处理下线，需要关闭通道，从集合中移除通道，最后还要在选择器里面取消注册
                        System.out.println(sChannel.getRemoteAddress() + "下线");
                        sChannel.close();
                        channels.remove(sChannel);
                        sk.cancel();
                    }
                }
                it.remove();
            }
        }
    }
}
```
主要是客户端
```
public class Client {
    public static void main(String[] args) throws Exception {
        SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 9999));
        sChannel.configureBlocking(false);
        Selector selector = Selector.open();
        sChannel.register(selector, SelectionKey.OP_READ);
        ByteBuffer writeBuf = ByteBuffer.allocate(1024);
        `// 客户端即需要输入消息，又需要接收消息，输入消息是阻塞操作，所以不能和接收消息放在同一线程内，`
 `// 必须为接收消息单独开一个线程`
        Runnable receive = () -> {
            try {
                ByteBuffer readBuf = ByteBuffer.allocate(1024);
                while (selector.select() > 0) {
                    Iterator<SelectionKey> it = selector.selectedKeys().iterator();
                    while (it.hasNext()) {
                        SelectionKey sk = it.next();
                        if (sk.isReadable()) {
                            SocketChannel socketChannel = (SocketChannel) sk.channel();
                            int len = 0;
                            while ((len = socketChannel.read(readBuf)) > 0) {
                                readBuf.flip();
                                System.out.println(new String(readBuf.array(), 0, len));
                                readBuf.clear();
                            }
                        }
                        it.remove();
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        };
        new Thread(receive).start();
        //4. 发送数据给服务端
        Scanner scan = new Scanner(System.in);
        while (scan.hasNext()) {
            //这是一个会阻塞的输入操作
            String str = scan.nextLine();
            writeBuf.put((new SimpleDateFormat("yyyy/MM/dd HH:mm:ss").format(System.currentTimeMillis()) + ": "+ str).getBytes());
            writeBuf.flip();
            sChannel.write(writeBuf);
            writeBuf.clear();
        }
        //5. 关闭通道
        sChannel.close();
    }
}
```

