from PIL import Image
import os

class Steganography:
    def __init__(self):
        self.END_MARKER = '1111111111111110' # 结束符

    def hide(self, image_path, secret_text, output_path):
        try:
            img = Image.open(image_path)
            # 兼容 RGBA
            img = img.convert('RGBA')
            
            # 转二进制
            binary_text = ''.join(format(ord(i), '08b') for i in secret_text) + self.END_MARKER
            
            pixels = list(img.getdata())
            new_pixels = []
            idx = 0
            
            for p in pixels:
                if idx < len(binary_text):
                    # 修改 R 分量最低位
                    r = p[0] & ~1 | int(binary_text[idx])
                    new_pixels.append((r, p[1], p[2], p[3]))
                    idx += 1
                else:
                    new_pixels.append(p)
            
            img.putdata(new_pixels)
            img.save(output_path, "PNG") # 必须 PNG
            return True
        except Exception as e:
            print(f"Stego Error: {e}")
            return False

    def extract(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.convert('RGBA')
            pixels = list(img.getdata())
            binary_data = ""
            
            for p in pixels:
                binary_data += str(p[0] & 1)
            
            all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
            decoded_text = ""
            for byte in all_bytes:
                if byte == self.END_MARKER[:8]:
                    if len(decoded_text) > 0: break 
                if byte == '11111110': break
                decoded_text += chr(int(byte, 2))
                if len(decoded_text) > 1000: break
                
            return decoded_text if decoded_text else "无隐写信息"
        except: return "提取失败"