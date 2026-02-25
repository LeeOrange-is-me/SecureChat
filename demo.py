from tkinter import LEFT, Text
from manim import *

# 配置：设置背景颜色等
config.background_color = "#1e1e1e"

class S1_Architecture(Scene):
    def construct(self):
        # --- 1. 角色定义 ---
        alice = Circle(color=BLUE, fill_opacity=0.5).shift(LEFT * 4 + DOWN * 1)
        alice_label = Text("Alice", font_size=24).next_to(alice, DOWN)
        
        bob = Circle(color=GREEN, fill_opacity=0.5).shift(RIGHT * 4 + DOWN * 1)
        bob_label = Text("Bob", font_size=24).next_to(bob, DOWN)
        
        server = Square(color=RED, fill_opacity=0.5).shift(UP * 2)
        server_icon = Text("☁️ Cloud Server", font_size=24).next_to(server, UP)
        
        # 锁的图标 (表示 Zero Knowledge)
        lock = Text("🔒", font_size=40).move_to(server)

        self.play(FadeIn(alice), Write(alice_label), FadeIn(bob), Write(bob_label))
        self.play(DrawBorderThenFill(server), Write(server_icon))
        self.play(GrowFromCenter(lock))
        
        # --- 2. 标题 ---
        title = Text("SecureChat System Architecture", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # --- 3. 连接线 ---
        line_a_s = Line(alice.get_top(), server.get_left(), color=GREY)
        line_s_b = Line(server.get_right(), bob.get_top(), color=GREY)
        
        self.play(Create(line_a_s), Create(line_s_b))
        
        # --- 4. 强调服务器不可见 ---
        self.wait(1)
        blind_text = Text("Server knows NOTHING", color=RED, font_size=24).next_to(server, RIGHT)
        self.play(Write(blind_text))
        self.play(Indicate(lock, color=RED))
        
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))

class SecureChatHashDemo(Scene):
    def construct(self):

        # ==============================
        # 1. 标题页
        # ==============================
        title = Text("SecureChat security password", font_size=42)
        subtitle = Text("Salted Hash", font_size=30)
        subtitle.next_to(title, DOWN)

        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))


        # ==============================
        # 2. 为什么不能存明文
        # ==============================
        section1 = Text("Why not plaintext?", font_size=36)
        section1.to_edge(UP)
        self.play(Write(section1))
        self.wait(1)

        pwd = Text("password：123456", color=RED)
        pwd.shift(UP)

        db_box = Rectangle(width=4, height=1)
        db_box.shift(DOWN*2)
        db_label = Text("Database", font_size=24)
        db_label.move_to(db_box.get_center())

        arrow = Arrow(pwd.get_bottom(), db_box.get_top())

        warning = Text("Once database is leaked, \n all passwords are exposed!", color=RED, font_size=20)
        warning.to_edge(DOWN)

        self.play(FadeIn(pwd))
        self.play(Create(db_box), Write(db_label))
        self.play(GrowArrow(arrow))
        self.play(Write(warning))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))


        # ==============================
        # 3. 哈希函数
        # ==============================
        section2 = Text("Security 1 - Hash", font_size=36)
        section2.to_edge(UP)
        self.play(Write(section2))
       
        self.wait(1)

        input_pwd = Text("123456", color=YELLOW).shift(LEFT*3)

        hash_box = Square(2)
        hash_box.set_color(BLUE)

        hash_text = Text("Hash func", font_size=20)
        hash_text.move_to(hash_box.get_center())

        output_hash = Text("e10adc3949ba59ab...", font_size=24, color=GREEN)
        output_hash.shift(RIGHT*3)

        self.play(FadeIn(input_pwd))
        self.play(Create(hash_box), Write(hash_text))
        self.play(FadeIn(output_hash))

        explain = Text("we can only compute hash from password, not reverse it", font_size=24)
        explain.to_edge(DOWN)

        self.play(Write(explain))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))


        # ==============================
        # 4. 为什么要加盐
        # ==============================
        section3 = Text("Security 2 - Salt", font_size=36)
        section3.to_edge(UP)
        self.play(Write(section3))
        self.wait(1)

        alice = Text("Alice password：123456", font_size=28).shift(UP)
        bob = Text("Bob   password：123456", font_size=28).shift(DOWN)

        self.play(FadeIn(alice), FadeIn(bob))
        self.wait(1)

        same_hash = Text("same password -> same hash (WARNING!)", color=RED)
        same_hash.to_edge(RIGHT)

        self.play(Write(same_hash))
        self.wait(2)
        self.play(FadeOut(same_hash))

        alice.shift(LEFT*3 + UP)
        bob.shift(LEFT*3 + DOWN)
        
        salt_a = Text("+ Salt_A", color=BLUE).next_to(alice, RIGHT)
        salt_b = Text("+ Salt_B", color=BLUE).next_to(bob, RIGHT)

        self.play(Write(salt_a), Write(salt_b))
        self.wait(1)

        result_a = Text("-> Hash_A", color=GREEN).next_to(salt_a, RIGHT)
        result_b = Text("-> Hash_B", color=GREEN).next_to(salt_b, RIGHT)

        self.play(Write(result_a), Write(result_b))

        diff = Text("same password + different salt = different hash", color=GREEN)
        diff.to_edge(ORIGIN)

        self.play(Write(diff))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))


        # ==============================
        # 5. 数据库存什么
        # ==============================
        section4 = Text("Single Demo", font_size=36)
        section4.to_edge(UP)
        self.play(Write(section4))
        self.wait(1)

        code_text = Text(
"""CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password_hash BLOB,
    salt BLOB
);""",
            font="Consolas",
            font_size=24
        )

        code_text.next_to(section4, DOWN)

        highlight = Text("So only hash( password + salt ) \n is stored in database \n rather than the plain password", color=YELLOW)
        highlight.to_edge(DOWN)

        self.play(FadeIn(code_text))
        self.play(Write(highlight))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))


        # ==============================
        # 6. 登录验证流程
        # ==============================
        section5 = Text("so how can we log in", font_size=36)
        section5.to_edge(UP)
        self.play(Write(section5))
        self.wait(1)

        step1 = Text("1. input password", font_size=28)
        step2 = Text("2. get Salt", font_size=28)
        step3 = Text("3. calculate Hash(password + Salt)", font_size=28)
        step4 = Text("4. compare Hash", font_size=28)

        steps = VGroup(step1, step2, step3, step4)
        steps.arrange(DOWN, aligned_edge=LEFT)
        steps.next_to(section5, DOWN, buff=0.8)

        self.play(Write(steps), run_time=4)

        final_text = Text("Server can verify password correctness \n without ever knowing the actual password!", 
                          font_size=32, color=GREEN)
        final_text.to_edge(DOWN)

        self.play(Write(final_text))
        self.wait(4)
   
class SecureChatArchitecture(Scene):
    def construct(self):

        # ==============================
        # 1. 总体设计思想
        # ==============================

        title = Text("Overall Design: Zero-Trust Architecture", font_size=40)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait(1)

        client_left = Rectangle(width=3.5, height=2.5, color=BLUE)
        client_left.shift(LEFT*4+UP*0.5)
        client_left_label = Text("Client (Alice)", font_size=24)
        client_left_label.move_to(client_left.get_center())

        client_right = Rectangle(width=3.5, height=2.5, color=BLUE)
        client_right.shift(RIGHT*4+UP*0.5)
        client_right_label = Text("Client (Bob)", font_size=24)
        client_right_label.move_to(client_right.get_center())

        server = Rectangle(width=4, height=3, color=RED)
        server.shift(UP*0.5)
        server_label = Text("Cloud Server\n(Honest-but-Curious)", font_size=24)
        server_label.move_to(server.get_center()+UP*0.5)

        self.play(Create(client_left), Write(client_left_label))
        self.play(Create(client_right), Write(client_right_label))
        self.play(Create(server), Write(server_label))

        self.wait(2)

        zero_text = Text(
            "Server can route and compute,\nbut cannot read plaintext.",
            font_size=28,
            color=YELLOW
        )
        zero_text.to_edge(DOWN)

        self.play(Write(zero_text))
        self.wait(3)
        self.play(FadeOut(zero_text))


        # ==============================
        # 2. 三层结构
        # ==============================

        layer_title = Text("Three Core Components", font_size=36)
        layer_title.to_edge(UP)

        self.play(Transform(title, layer_title))

        client_role = Text(
            "Client:\n- AES Encryption\n- HMAC Trapdoor\n- Local Decryption",
            font_size=16
        )
        client_role.next_to(client_left, DOWN)

        server_role = Text(
            "Server:\n- WebSocket Routing\n- Trapdoor Matching\n- Homomorphic Addition",
            font_size=16
        )
        server_role.next_to(server, DOWN)

        db = Rectangle(width=3, height=1.5, color=GREEN)
        db.move_to(ORIGIN+DOWN*0.05)
        db_label = Text("SQLite Database\nEncrypted Storage", font_size=16)
        db_label.move_to(db.get_center())
        

        self.play(Write(client_role))
        self.play(Write(server_role))
        self.play(Create(db), Write(db_label))

        self.wait(3)


        # ==============================
        # 3. 数据流演示（Alice 发消息）
        # ==============================

        self.play(FadeOut(client_role), FadeOut(server_role))

        flow_title = Text("Message Flow: Alice -> Bob", font_size=16)
        flow_title.to_edge(DOWN*2+LEFT*2)
        self.play(Transform(layer_title, flow_title))

        # Step 1 输入
        message = Text('"Hello"', color=WHITE,font_size=14)
        message.move_to(client_left.get_center()+DOWN*1)

        self.play(FadeIn(message))
        self.wait(1)

        # Step 2 加密
        encrypted = Text("AES -> U2FsdX1...", color=YELLOW,font_size=14)
        encrypted.move_to(client_left.get_center()+DOWN*1)

        self.play(Transform(message, encrypted))
        self.wait(1)

        # Step 3 传输到服务器
        arrow1 = Arrow(client_left.get_right(), server.get_left())
        self.play(GrowArrow(arrow1))
        self.play(message.animate.move_to(server.get_center()+DOWN*1))
        self.wait(1)

        # Step 4 存数据库
        arrow2 = Arrow(server.get_bottom(), db.get_top())
        self.play(GrowArrow(arrow2))
        self.wait(1)

        # Step 5 推送到 Bob
        arrow3 = Arrow(server.get_right(), client_right.get_left())
        self.play(GrowArrow(arrow3))
        self.play(message.animate.move_to(client_right.get_center()+DOWN*1))
        self.wait(1)

        # Step 6 解密
        decrypted = Text('"Hello"', color=GREEN, font_size=14)
        decrypted.move_to(client_right.get_center()+DOWN*1)
        self.play(Transform(message, decrypted))
        self.wait(2)


        # ==============================
        # 4. 总结
        # ==============================

        summary = Text(
            "Server executes perfectly,\nbut knows nothing about the content.",
            font_size=30,
            color=GREEN
        )

        self.play(FadeOut(message), FadeOut(arrow1),
                  FadeOut(arrow2), FadeOut(arrow3))

        summary.move_to(DOWN*2.5)
        self.play(Write(summary))
        self.wait(4)


class SecureChatE2EE(Scene):
    def construct(self):
        # --- 1. E2EE 核心理念 ---
        title = Text("SecureChat: True End-to-End Encryption", color=BLUE).scale(0.7).to_edge(UP)
        
        # 创建用户节点 (用圆圈和文字代替)
        alice = VGroup(Circle(radius=0.3, color=WHITE), Text("Alice").scale(0.4)).arrange(DOWN)
        server = VGroup(Square(side_length=0.7, color=GRAY, fill_opacity=0.5), Text("Server").scale(0.4)).arrange(DOWN)
        bob = VGroup(Circle(radius=0.3, color=WHITE), Text("Bob").scale(0.4)).arrange(DOWN)
        
        nodes = VGroup(alice, server, bob).arrange(RIGHT, buff=2)
        self.play(Write(title), FadeIn(nodes))

        # 模拟消息：Hello World
        msg_rect = RoundedRectangle(corner_radius=0.1, height=0.4, width=1.2, color=GREEN)
        msg_text = Text("Hello", color=GREEN).scale(0.3).move_to(msg_rect)
        msg = VGroup(msg_rect, msg_text).next_to(alice, UP)
        
        self.play(Write(msg))
        
        # 加密过程 (变成红色乱码)
        cipher_rect = RoundedRectangle(corner_radius=0.1, height=0.4, width=1.2, color=RED)
        cipher_text = Text("U2Fsd...", color=RED).scale(0.3).move_to(cipher_rect)
        lock = Text("🔒").scale(0.4).next_to(cipher_rect, UP)
        
        self.play(Transform(msg, VGroup(cipher_rect, cipher_text)), FadeIn(lock))
        
        # 经过服务器 (服务器看不懂)
        self.play(msg.animate.move_to(server.get_center() + UP*0.8), lock.animate.move_to(server.get_center() + UP*1.1))
        q_mark = Text("?", color=RED).scale(1.2).next_to(server[0], RIGHT)
        self.play(Write(q_mark))
        self.wait(0.5)
        self.play(FadeOut(q_mark))
        
        # 到达 Bob 并解密
        self.play(msg.animate.move_to(bob.get_center() + UP*0.8), lock.animate.move_to(bob.get_center() + UP*1.1))
        self.play(Transform(msg, VGroup(msg_rect.copy(), msg_text.copy())), FadeOut(lock))
        self.wait(1)
        self.clear()

        # --- 2. AES 性能优势 (无 LaTeX 坐标轴) ---
        perf_title = Text("Why AES? Performance (Latency)", color=YELLOW).scale(0.7).to_edge(UP)
        self.play(Write(perf_title))

        axes = Axes(
            x_range=[0, 3, 1], y_range=[0, 100, 20],
            x_length=6, y_length=4,
            axis_config={"include_tip": False}
        ).shift(DOWN*0.5)
        
        # 手动创建标签避开 LaTeX
        x_label = Text("Algorithm").scale(0.4).next_to(axes.x_axis, DOWN)
        y_label = Text("Latency (ms)").scale(0.4).rotate(90*DEGREES).next_to(axes.y_axis, LEFT)
        
        aes_bar = Rectangle(width=1, height=0.1, color=GREEN, fill_opacity=0.8).move_to(axes.c2p(1, 0), aligned_edge=DOWN)
        rsa_bar = Rectangle(width=1, height=3.5, color=RED, fill_opacity=0.8).move_to(axes.c2p(2, 0), aligned_edge=DOWN)
        
        aes_txt = Text("AES").scale(0.4).next_to(aes_bar, DOWN)
        rsa_txt = Text("RSA").scale(0.4).next_to(rsa_bar, DOWN)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(Create(aes_bar), Write(aes_txt))
        self.play(Create(rsa_bar), Write(rsa_txt))
        
        note = Text("1000x Faster", color=GOLD).scale(0.6).next_to(rsa_bar, UP)
        self.play(Write(note))
        self.wait(2)


class  SecureSearchSSE(Scene):
    def construct(self):
        # --- 1. 抛出痛点：加密与搜索的“死结” ---
        title = Text("SSE: Symmetric Searchable Encryption", color=BLUE).scale(0.8).to_edge(UP)
        self.add(title)

        # 场景：服务器里满是加密锁
        server_area = RoundedRectangle(corner_radius=0.2, height=4, width=5, color=GRAY_B, fill_opacity=0.1)
        server_label = Text("Untrusted Server (Database)").scale(0.4).next_to(server_area, DOWN)
        
        locks = VGroup(*[Text("🔒").scale(0.5) for _ in range(12)]).arrange_in_grid(3, 4, buff=0.5).move_to(server_area)
        
        self.play(Create(server_area), FadeIn(server_label), FadeIn(locks))
        
        # 痛点文字
        paradox = Text("The E2EE Paradox:", color=RED).scale(0.6).to_edge(LEFT, buff=0.5).shift(UP*1)
        paradox_sub = Text("If data is blind to the server,\nhow can we search it?", font_size=24).next_to(paradox, DOWN, aligned_edge=LEFT)
        
        self.play(Write(paradox), Write(paradox_sub))
        self.wait(2)
        self.play(FadeOut(paradox), FadeOut(paradox_sub), FadeOut(locks))

        # --- 2. 核心原理：陷门 (Trapdoor) 与安全索引 ---
        # 模拟“图书馆”比喻
        book_box = Square(side_length=1, color=RED, fill_opacity=0.5).move_to(server_area.get_center())
        box_label = Text("Encrypted Message", color=RED).scale(0.3).next_to(book_box, DOWN)
        
        # 贴上“暗号”标签 (Secure Index)
        secure_index = Text("♈︎ (a1b2c3...)", color=GOLD).scale(0.6).move_to(book_box)
        
        self.play(DrawBorderThenFill(book_box), Write(box_label))
        self.wait(1)
        self.play(Write(secure_index))
        self.play(Indicate(secure_index, color=GOLD))
        
        principle_text = Text("Principle: The server matches 'Patterns',\nnot 'Meanings'.", color=GOLD, font_size=16).to_edge(LEFT, buff=0.5)
        self.play(Write(principle_text))
        self.wait(2)
        self.play(FadeOut(principle_text), FadeOut(book_box), FadeOut(box_label), FadeOut(secure_index))

        # --- 3. 数据流转：一条消息的旅程 ---
        # 重置画布，展示 Client 和 Server
        client_node = VGroup(Circle(radius=0.4, color=WHITE), Text("Alice's Browser").scale(0.35)).arrange(DOWN).to_edge(LEFT, buff=1)
        server_node = VGroup(Square(side_length=1.2, color=GRAY), Text("Server").scale(0.35)).arrange(DOWN).to_edge(RIGHT, buff=1)
        self.play(FadeIn(client_node), FadeIn(server_node))

        # 第一步：建库 (Indexing)
        raw_msg = Text('"Hello World"', color=GREEN).scale(0.4).next_to(client_node, UP)
        self.play(Write(raw_msg))
        
        # 分词视觉化 (Tokenization)
        tokens = VGroup(Text("Hello").scale(0.3), Text("World").scale(0.3)).arrange(RIGHT, buff=0.2).move_to(client_node)
        self.play(ReplacementTransform(raw_msg, tokens))
        self.wait(0.5)
        
        # 计算哈希 (HMAC-SHA256)
        hash_tag = Text("a1b2c3...", font="Monospace", color=GOLD).scale(0.35).move_to(tokens)
        self.play(Transform(tokens, hash_tag))
        
        # 发送到服务器存储
        self.play(tokens.animate.move_to(server_node[0].get_center()))
        index_stored_text = Text("search_index += 'a1b2c3...'", color=GOLD, font="Monospace").scale(0.3).next_to(server_node[0], UP)
        self.play(Write(index_stored_text))
        self.wait(1)

        # 第二步：铸剑 (Searching)
        search_input = Text("Search: 'Hello'", color=WHITE).scale(0.4).next_to(client_node, UP)
        self.play(Write(search_input))
        
        trapdoor = VGroup(
            RoundedRectangle(corner_radius=0.1, height=0.4, width=1.2, color=GOLD, fill_opacity=0.3),
            Text("a1b2c3...", font="Monospace", color=GOLD).scale(0.3)
        ).move_to(client_node)
        
        self.play(ReplacementTransform(search_input, trapdoor))
        self.wait(0.5)
        
        # 陷门飞向服务器 (Trapdoor Transfer)
        self.play(trapdoor.animate.move_to(server_node[0].get_center() + LEFT*0.4))

        # 第三步：盲配 (Matching)
        match_highlight = Indicate(server_node[0], color=GOLD, scale_factor=1.3)
        success_text = Text("SQL MATCH!", color=GREEN, font_size=12).scale(0.5).next_to(server_node[0], RIGHT)
        
        self.play(match_highlight)
        self.play(Write(success_text))
        
        # 返回结果 (Encrypted)
        result_box = Square(side_length=0.4, color=RED, fill_opacity=0.8).move_to(server_node[0])
        self.play(result_box.animate.move_to(client_node.get_center() + RIGHT*1))
        
        # 本地解密
        decrypted_res = Text('"Hello World"', color=GREEN).scale(0.4).move_to(result_box)
        self.play(Transform(result_box, decrypted_res))
        self.wait(2)
        self.clear()

        # --- 4. 安全价值：总结 ---
        pros_title = Text("Why is our SSE Secure?", color=GOLD).to_edge(UP)
        pros_list = VGroup(
            Text("1. Query Privacy: Server never sees the keyword.", font_size=30),
            Text("2. Data Privacy: Results remain encrypted on Server.", font_size=30),
            Text("3. Client-Driven: All Hashing & Tokenizing happens in JS.", font_size=30)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(ORIGIN)

        self.play(Write(pros_title))
        for item in pros_list:
            self.play(FadeIn(item, shift=RIGHT))
            self.wait(1)
        
        final_punchline = Text("Server = String Matching Engine (Blind)", color=BLUE_B).scale(0.6).to_edge(DOWN, buff=1)
        self.play(FadeIn(final_punchline, shift=UP))
        self.wait(3)
class S2_E2EE_Chat(Scene):
    def construct(self):
        title = Text("Feature 1: End-to-End Encryption (AES)", font_size=32).to_edge(UP)
        self.add(title)

        # 角色位置
        alice = Circle(color=BLUE, radius=0.5).shift(LEFT * 5)
        bob = Circle(color=GREEN, radius=0.5).shift(RIGHT * 5)
        server = Square(color=RED, side_length=1).shift(UP * 0)
        
        self.add(alice, bob, server)
        
        # --- 1. 明文消息 ---
        msg = Text("Hello World", font_size=24, color=WHITE).next_to(alice, UP)
        self.play(Write(msg))
        
        # --- 2. 加密过程 ---
        key = Text("🔑", font_size=24).next_to(msg, RIGHT)
        self.play(FadeIn(key))
        
        # 变成密文
        cipher = Text("U2FsdGVkX1...", font_size=24, color=YELLOW).move_to(msg)
        self.play(Transform(msg, cipher), FadeOut(key))
        
        # --- 3. 传输 ---
        # 移动到服务器
        self.play(msg.animate.move_to(server.get_center()))
        self.wait(0.5)
        
        # 服务器试图偷看 (失败)
        question = Text("?", color=RED).next_to(server, UP)
        self.play(FadeIn(question))
        self.play(Wiggle(server)) # 摇晃表示无法解析
        self.play(FadeOut(question))
        
        # 移动到 Bob
        self.play(msg.animate.next_to(bob, UP))
        
        # --- 4. 解密 ---
        key_bob = Text("🔑", font_size=24).next_to(msg, LEFT)
        self.play(FadeIn(key_bob))
        
        plaintext = Text("Hello World", font_size=24, color=WHITE).move_to(msg)
        self.play(Transform(msg, plaintext), FadeOut(key_bob))
        
        self.play(Indicate(msg, color=GREEN))
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))

class S3_SSE_Search(Scene):
    def construct(self):
        title = Text("Feature 2: Searchable Encryption (SSE)", font_size=32).to_edge(UP)
        self.add(title)
        
        # --- 1. 左侧：客户端 ---
        client_box = Rectangle(width=4, height=5, color=BLUE).shift(LEFT * 3)
        client_label = Text("Client", font_size=24).next_to(client_box, UP)
        
        # --- 2. 右侧：服务端索引表 ---
        server_box = Rectangle(width=4, height=5, color=RED).shift(RIGHT * 3)
        server_label = Text("Server Index", font_size=24).next_to(server_box, UP)
        
        index_data = VGroup(
            Text("Trapdoor: a8f3... -> Msg: 1", font_size=18),
            Text("Trapdoor: b2c9... -> Msg: 2", font_size=18),
            Text("Trapdoor: c4d1... -> Msg: 3", font_size=18),
        ).arrange(DOWN, aligned_edge=LEFT).move_to(server_box)
        
        self.add(client_box, client_label, server_box, server_label, index_data)
        
        # --- 3. 搜索动作 ---
        keyword = Text("Search: 'Secret'", font_size=24).move_to(client_box)
        self.play(Write(keyword))
        
        # 计算陷门 (Hash)
        trapdoor = Text("Trapdoor: b2c9...", font_size=24, color=YELLOW).move_to(client_box)
        self.play(Transform(keyword, trapdoor))
        self.wait(0.5)
        
        # 发送陷门
        self.play(trapdoor.animate.move_to(server_box.get_left() + RIGHT*0.5))
        
        # --- 4. 匹配过程 ---
        # 箭头指示匹配
        arrow = Arrow(trapdoor.get_right(), index_data[1].get_left(), color=YELLOW)
        self.play(GrowArrow(arrow))
        self.play(Indicate(index_data[1], color=YELLOW))
        
        # --- 5. 返回结果 ---
        result_text = Text("Found: Msg 2 (Encrypted)", font_size=20, color=GREEN).next_to(client_box, DOWN)
        self.play(Write(result_text))
        
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))

class S4_Privacy_Calc(Scene):
    def construct(self):
        title = Text("Feature 3: Privacy Computing (Homomorphic)", font_size=32).to_edge(UP)
        self.add(title)
        
        # 公式展示 E(m1) * E(m2) = E(m1 + m2)
        formula = MathTex(r"E(m_1) \cdot E(m_2) = E(m_1 + m_2)", font_size=40).shift(UP * 2)
        self.play(Write(formula))
        
        # 具体例子
        user1 = Text("User A: 100", font_size=24, color=BLUE).shift(LEFT * 3)
        user2 = Text("User B: 200", font_size=24, color=GREEN).shift(RIGHT * 3)
        
        self.play(FadeIn(user1), FadeIn(user2))
        
        # 加密
        enc1 = Text("Enc(100)", font_size=24).move_to(user1)
        enc2 = Text("Enc(200)", font_size=24).move_to(user2)
        
        self.play(Transform(user1, enc1), Transform(user2, enc2))
        
        # 发送到服务器计算
        server_zone = Circle(color=RED, fill_opacity=0.2).scale(1.5)
        server_label = Text("Cloud Calculation", font_size=20).next_to(server_zone, DOWN)
        
        self.play(Create(server_zone), Write(server_label))
        self.play(user1.animate.move_to(server_zone.get_left() + RIGHT),
                  user2.animate.move_to(server_zone.get_right() + LEFT))
        
        # 融合（同态加法）
        result_enc = Text("Enc(300)", font_size=30, color=YELLOW).move_to(server_zone)
        self.play(ReplacementTransform(VGroup(user1, user2), result_enc))
        
        # 服务器只看到密文
        unknown = Text("Value = ???", font_size=18, color=RED).next_to(result_enc, UP)
        self.play(Write(unknown))
        self.wait(1)
        self.play(FadeOut(unknown))
        
        # 返回并解密
        final_val = Text("Total: 300", font_size=30, color=WHITE).shift(DOWN * 2)
        self.play(result_enc.animate.move_to(DOWN * 2))
        
        key = Text("🗝️ Private Key", font_size=20).next_to(result_enc, RIGHT)
        self.play(FadeIn(key))
        self.play(Transform(result_enc, final_val), FadeOut(key))
        
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)))

class S5_Steganography(Scene):
    def construct(self):
        title = Text("Feature 4: Steganography (LSB)", font_size=32).to_edge(UP)
        self.add(title)
        
        # 模拟图片
        image_box = Square(side_length=3, color=WHITE, fill_opacity=0.2).shift(LEFT * 2)
        image_label = Text("Image.png", font_size=24).next_to(image_box, UP)
        
        # 秘密文字
        secret = Text("Secret Data", color=RED, font_size=24).shift(RIGHT * 3)
        binary = Text("010101...", font_size=18, color=YELLOW).next_to(secret, DOWN)
        
        self.play(Create(image_box), Write(image_label))
        self.play(Write(secret))
        
        # 文字转二进制
        self.play(Transform(secret, binary))
        
        # 嵌入过程
        self.play(secret.animate.move_to(image_box.get_center()))
        
        # 消失在图片中
        self.play(FadeOut(secret), image_box.animate.set_fill(opacity=0.3))
        
        # 结果：外观看起来没变
        result_label = Text("Looks Identical!", font_size=24, color=GREEN).next_to(image_box, DOWN)
        self.play(Write(result_label))
        
        self.wait(2)