"""
Gera o icon.ico do ErosGest AI
"""
import struct
import zlib
import os

def create_png_bytes(size):
    """Cria um PNG simples com o logo ErosGest"""
    width = height = size
    
    def write_chunk(chunk_type, data):
        chunk_len = struct.pack('>I', len(data))
        chunk_data = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk_data) & 0xffffffff)
        return chunk_len + chunk_data + crc
    
    # Pixel data: fundo roxo escuro com letra E branca
    pixels = []
    for y in range(height):
        row = [0]  # filter byte
        for x in range(width):
            # Gradiente de fundo: roxo escuro para roxo médio
            cx = x - width // 2
            cy = y - height // 2
            dist = (cx**2 + cy**2) ** 0.5
            max_dist = (width // 2) * 1.414
            
            # Fundo gradiente roxo
            r = int(30 + (cx + width//2) / width * 40)
            g = int(10 + (cy + height//2) / height * 20)
            b = int(80 + dist / max_dist * 60)
            
            # Desenha "E" estilizado
            margin = int(width * 0.25)
            thick = max(2, width // 16)
            mid_y = height // 2
            
            in_E = False
            # Barra vertical esquerda
            if margin <= x <= margin + thick and margin <= y <= height - margin:
                in_E = True
            # Barra horizontal topo
            elif margin <= x <= width - margin - thick and margin <= y <= margin + thick:
                in_E = True
            # Barra horizontal meio
            elif margin <= x <= width - margin - thick*2 and mid_y - thick//2 <= y <= mid_y + thick//2:
                in_E = True
            # Barra horizontal base
            elif margin <= x <= width - margin - thick and height - margin - thick <= y <= height - margin:
                in_E = True
            
            if in_E:
                row.extend([255, 220, 255, 255])  # branco/lilás
            else:
                row.extend([r, g, b, 255])
        pixels.append(bytes(row))
    
    import zlib
    raw = b''.join(pixels)
    compressed = zlib.compress(raw, 9)
    
    # PNG header
    png = b'\x89PNG\r\n\x1a\n'
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # 8-bit, RGBA... 
    # Actually let's use RGBA (color type 6)
    ihdr_data = struct.pack('>II', width, height) + bytes([8, 6, 0, 0, 0])
    png += write_chunk(b'IHDR', ihdr_data)
    # IDAT
    png += write_chunk(b'IDAT', compressed)
    # IEND
    png += write_chunk(b'IEND', b'')
    
    return png

# Generate ICO with multiple sizes
sizes = [16, 32, 48, 64, 128, 256]

# Use PIL if available, otherwise create a simple placeholder
try:
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    images = []
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Fundo gradiente circular roxo
        for y in range(size):
            for x in range(size):
                cx = x - size // 2
                cy = y - size // 2
                dist = (cx**2 + cy**2) ** 0.5
                if dist <= size // 2:
                    # Gradiente roxo
                    t = dist / (size // 2)
                    r = int(45 + t * 20)
                    g = int(10 + t * 15)
                    b = int(120 - t * 30)
                    alpha = 255
                    img.putpixel((x, y), (r, g, b, alpha))
        
        # Letra E estilizada
        margin = size // 5
        thick = max(2, size // 10)
        mid = size // 2
        
        color = (220, 180, 255, 255)
        # Vertical
        draw.rectangle([margin, margin, margin + thick, size - margin], fill=color)
        # Top
        draw.rectangle([margin, margin, size - margin, margin + thick], fill=color)
        # Mid  
        draw.rectangle([margin, mid - thick//2, size - margin - thick, mid + thick//2], fill=color)
        # Bottom
        draw.rectangle([margin, size - margin - thick, size - margin, size - margin], fill=color)
        
        images.append(img)
    
    # Save as ICO
    output_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(output_path, format='ICO', sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Icon created: {output_path}")

except ImportError:
    print("PIL not found, creating minimal ICO...")
    # Create minimal valid ICO file
    size = 32
    output_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    
    # Minimal ICO: 1 image, 32x32, 32bpp
    # ICO header
    ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved, type=1(ICO), count=1
    
    # Image directory entry
    width_byte = size if size < 256 else 0
    height_byte = size if size < 256 else 0
    color_count = 0
    reserved = 0
    planes = 1
    bit_count = 32
    image_offset = 22  # 6 (header) + 16 (one dir entry)
    
    # Create BMP data for 32x32 RGBA
    bmp_header_size = 40
    pixel_data_size = size * size * 4
    bmp_size = bmp_header_size + pixel_data_size
    
    dir_entry = struct.pack('<BBBBHHII',
        width_byte, height_byte, color_count, reserved,
        planes, bit_count, bmp_size, image_offset)
    
    # BMP INFOHEADER
    bmp_header = struct.pack('<IiiHHIIiiII',
        bmp_header_size, size, size * 2, 1, 32, 0,
        pixel_data_size, 0, 0, 0, 0)
    
    # Pixel data (BGRA)
    pixels = bytearray()
    for y in range(size - 1, -1, -1):  # BMP is bottom-up
        for x in range(size):
            cx = x - size // 2
            cy = y - size // 2
            dist = (cx**2 + cy**2) ** 0.5
            
            if dist <= size // 2:
                r, g, b, a = 45, 10, 120, 255
            else:
                r, g, b, a = 0, 0, 0, 0
            pixels.extend([b, g, r, a])  # BGRA
    
    with open(output_path, 'wb') as f:
        f.write(ico_header + dir_entry + bmp_header + bytes(pixels))
    
    print(f"Minimal icon created: {output_path}")

if __name__ == '__main__':
    pass
