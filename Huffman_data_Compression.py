from collections import Counter
import heapq
from pathlib import Path


# 1. Mỗi nút lưu tần suất, ký hiệu byte và hai nút con.
class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right


# 2. Xây cây Huffman: luôn ghép hai nút nhỏ nhất (tham lam).
def build_tree(freq):
    heap = []
    order = 0  # Tránh lỗi so sánh hai Node khi tần suất bằng nhau.

    for symbol, count in sorted(freq.items()):
        heapq.heappush(heap, (count, order, Node(count, symbol)))
        order += 1

    if not heap:  # Tệp rỗng.
        return None

    while len(heap) > 1:
        count1, _, left = heapq.heappop(heap)
        count2, _, right = heapq.heappop(heap)
        parent = Node(count1 + count2, left=left, right=right) #nút cha bằng tổng tần suất hai nút con
        heapq.heappush(heap, (parent.freq, order, parent))
        order += 1

    return heap[0][2]  # Nút cuối cùng là gốc cây.


# 3. Đi nhánh trái ghi 0, nhánh phải ghi 1 để sinh mã.
def build_codes(node, code="", result=None):
    if result is None:
        result = {}
    if node is None:
        return result
    if node.symbol is not None:  # Đã tới nút lá.
        result[node.symbol] = code or "0"  # Tệp chỉ có 1 loại byte.
        return result
    build_codes(node.left, code + "0", result)
    build_codes(node.right, code + "1", result)
    return result


# 4. Nén tệp: đếm tần suất, tạo mã, ghi bit vào tệp .huff.
def compress(input_file, output_file):
    data = Path(input_file).read_bytes()  # Đọc byte để hỗ trợ tiếng Việt UTF-8.
    freq = Counter(data)                 # Đếm số lần mỗi byte xuất hiện.
    codes = build_codes(build_tree(freq))

    with open(output_file, "wb") as f:
        # Phần đầu tệp giúp giải nén tái tạo lại đúng cây Huffman.
        f.write(b"HUF1")  # Dấu nhận biết định dạng.
        f.write(len(freq).to_bytes(2, "big"))  # Số byte khác nhau.
        for symbol, count in sorted(freq.items()):
            f.write(bytes([symbol]))           # Giá trị byte: 1 byte.
            f.write(count.to_bytes(8, "big"))  # Tần suất: 8 byte.

        buffer, used = 0, 0
        for symbol in data:
            for bit in codes[symbol]:
                buffer = (buffer << 1) | int(bit)  # Thêm 1 bit vào bộ đệm.
                used += 1
                if used == 8:  # Gom đủ 8 bit thành 1 byte để ghi.
                    f.write(bytes([buffer]))
                    buffer, used = 0, 0
        if used:  # Các bit 0 cuối chỉ để đủ 8 bit.
            f.write(bytes([buffer << (8 - used)]))

    print("Đã nén:", input_file, "->", output_file)
    print("Kích thước:", len(data), "->", Path(output_file).stat().st_size, "byte")


# 5. Giải nén tệp
def decompress(input_file, output_file):

    # Doc tep da nen
    with open(input_file, "rb") as f:

        # Kiểm tra xem tệp có đúng định dạng Huffman không
        if f.read(4) != b"HUF1":
            raise ValueError("Tep khong dung dinh dang Huffman!")

        # Đọc số luợng byte khác nhau trong bảng tần suất
        header = f.read(2)
        if len(header) != 2:
            raise ValueError("Tep nen bi thieu du lieu!")

        k = int.from_bytes(header, "big")
        if k > 256:
            raise ValueError("Bang tan suat khong hop le!")

        # Đọc bảng tần suất đã lưu khi nén
        freq = {}
        for _ in range(k):
            symbol = f.read(1)
            count = f.read(8)

            if len(symbol) != 1 or len(count) != 8:
                raise ValueError("Bang tan suat bi thieu!")

            freq[symbol[0]] = int.from_bytes(count, "big")

        # Đọc phần dữ liệu đã nén
        encoded = f.read()

    # Dựng lại cây Huffman từ bảng tần suất
    root = build_tree(freq)

    # Tổng số byte gốc để kiểm tra khi giải nén
    total = sum(freq.values())

    # Noi luu du lieu sau khi giai nen
    result = bytearray()

    if root is None:
        pass  # Truong hop tep rong

    elif root.symbol is not None:
        # Truong hop tep chi co mot loai byte
        result.extend([root.symbol] * total)

    else:
        # Duyet tung bit de giai ma
        node = root

        for byte in encoded:
            for i in range(7, -1, -1):

                # Bit 0 di trai, bit 1 di phai
                bit = (byte >> i) & 1
                node = node.left if bit == 0 else node.right

                if node is None:
                    raise ValueError("Du lieu nen bi loi!")

                # Gap nut la thi lay byte goc
                if node.symbol is not None:
                    result.append(node.symbol)
                    node = root

                    # Du byte goc thi dung
                    if len(result) == total:
                        break

            if len(result) == total:
                break

    # Kiem tra da giai nen du du lieu chua
    if len(result) != total:
        raise ValueError("Khong giai nen du du lieu!")

    # Ghi du lieu goc thanh tep .txt
    Path(output_file).write_bytes(result)

    print("Da giai nen:", input_file, "->", output_file)
    print("Kich thuoc sau giai nen:", len(result), "byte")


# 6. Chạy chương trình nén
# Gọi hàm nén.

if __name__ == "__main__":

#Gọi hàm nén văn bản
    # Tep van ban ban dau
    # input_file = "test_file.compressed"

    # # Tep duoc tao ra sau khi nen Huffman
    # output_file = "test_file_decompressed.txt"

    # # Goi ham nen da viet o phia tren
    # compress(input_file, output_file)

    # print("Chuong trinh da chay xong!")

#Gọi hàm giải nén văn bản
    # Tên tệp đã được nén
    compressed_input = "test_file.compressed"

    # Tên tệp sẽ được giải nén
    decompressed_output = "test_file_decompressed.txt"

    # Gọi hàm giải nén
    decompress(compressed_input, decompressed_output)
    print("Chuong trinh da chay xong!")