import sys
import os

def read_uint32(p, pos):
    if pos + 4 > len(p):
        return None, pos
    val = int.from_bytes(p[pos:pos+4], byteorder='little')
    return val, pos + 4

def align4(length):
    return (4 - (length % 4)) % 4

def parse_snss(filepath):
    with open(filepath, 'rb') as f:
        p = f.read()
    
    if not p.startswith(b'SNSS'):
        print(f"[-] {filepath} is not a valid SNSS session file.")
        return

    pos = 8 # Skip magic and version
    urls = []

    while pos < len(p):
        if pos + 3 > len(p):
            break
        size = int.from_bytes(p[pos:pos+2], byteorder='little')
        cmd_id = p[pos+2]
        pos += 3

        payload_end = pos + size - 1
        if payload_end > len(p):
            break
        
        payload = p[pos:payload_end]
        
        # Command ID 6 typically represents tab navigation data containing URLs
        if cmd_id == 6 and len(payload) > 8:
            sub_pos = 8 # skip tab id and navigation index
            length, sub_pos = read_uint32(payload, sub_pos)
            if length and sub_pos + length <= len(payload):
                url_bytes = payload[sub_pos:sub_pos+length]
                try:
                    url = url_bytes.decode('utf-8', errors='ignore')
                    if url.startswith('http://') or url.startswith('https://'):
                        urls.append(url)
                except Exception:
                    pass

        pos = payload_end

    print(f"\n[+] Extracted {len(urls)} URLs from {os.path.basename(filepath)}:")
    for u in sorted(set(urls)):
        print(u)

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else input("Enter path to session file: ").strip()
    parse_snss(target)
