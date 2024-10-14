import tkinter as tk
import random
import pyttsx3
import pandas as pd

# Khởi tạo engine đọc phát âm
engine = pyttsx3.init()

# Thiết lập giọng Anh Mỹ
voices = engine.getProperty('voices')
for voice in voices:
    if 'en_US' in voice.id:  # Tìm giọng đọc tiếng Anh Mỹ
        engine.setProperty('voice', voice.id)
        break

# Điều chỉnh âm lượng và tốc độ đọc
default_rate = engine.getProperty('rate')  # Lấy tốc độ mặc định
new_rate = int(default_rate * 0.9)  # Giảm 10% tốc độ
engine.setProperty('rate', new_rate)  # Cài đặt tốc độ mới
engine.setProperty('volume', 1.0)  # Âm lượng

# Khởi tạo file để ghi các từ sai
wrong_words_file = "sai.txt"

# Đọc dữ liệu từ file Excel
def load_words_from_excel(file_path):
    df = pd.read_excel(file_path)  # Đọc file Excel
    words = df['Words'].tolist()   # Giả sử cột chứa từ có tên 'Words'
    return words

# Ghi từ sai vào file .txt, ngăn cách bằng dấu chấm
def log_wrong_word(word):
    with open(wrong_words_file, "a") as file:
        file.write(f"{word}. ")

# Phát âm từ
def speak_word(word):
    engine.say(word)
    engine.runAndWait()

# Hàm kiểm tra từ
def check_word(event=None):
    entered_word = entry.get().replace(" ", "").lower()  # Bỏ khoảng trắng và chuyển chữ thường
    word_to_compare = current_word.replace(" ", "").lower()  # Bỏ khoảng trắng và chuyển chữ thường
    
    if entered_word == word_to_compare:
        result_label.config(text="Đúng!")
        root.after(1000, next_word)  # Delay 3 giây trước khi đọc từ mới
    else:
        result_label.config(text="Sai, hãy thử lại.")
        log_wrong_word(current_word)  # Ghi từ sai vào file .txt
        entry.delete(0, tk.END)

# Hàm để đọc lại từ
def repeat_word(event=None):
    speak_word(current_word)

# Hàm bỏ qua từ hiện tại
def skip_word(event=None):
    result_label.config(text=f"Từ bạn bỏ qua là: {current_word}")
    root.after(1000, next_word)  # Tạm dừng 2 giây trước khi chuyển sang từ mới

# Hàm chọn từ mới
def next_word():
    global current_word
    current_word = random.choice(words_list)
    entry.delete(0, tk.END)
    result_label.config(text="")  # Xóa thông báo trước
    speak_word(current_word)

# Đọc danh sách từ từ file Excel
file_path = 'words.xlsx'  # Đường dẫn đến file Excel của bạn
words_list = load_words_from_excel(file_path)

# Tạo giao diện tkinter
root = tk.Tk()
root.title("Luyện nghe và đánh máy tiếng Anh")

# Đặt cửa sổ ở giữa màn hình
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Tạo các thành phần giao diện
label = tk.Label(root, text="Hãy nhập từ bạn nghe thấy:")
label.pack(pady=10)

entry = tk.Entry(root, font=('Arial', 14))
entry.pack(pady=10)

# Button "Kiểm tra"
button_check = tk.Button(root, text="Kiểm tra", command=check_word)
button_check.pack(pady=10)

# Button "Đọc lại"
button_repeat = tk.Button(root, text="Đọc lại", command=repeat_word)
button_repeat.pack(pady=10)

# Button "Không biết"
button_skip = tk.Button(root, text="Không biết", command=skip_word)
button_skip.pack(pady=10)

# Nhãn hiển thị kết quả "Đúng", "Sai" hoặc "Từ bỏ qua"
result_label = tk.Label(root, text="", font=('Arial', 14))
result_label.pack(pady=10)

# Gán phím tắt
root.bind('<Return>', check_word)  # Phím Enter để kiểm tra
root.bind('<Control_L>', repeat_word)  # Phím Ctrl để đọc lại từ
root.bind('<Shift_L>', skip_word)  # Phím Shift để bỏ qua từ hiện tại

# Bắt đầu với từ đầu tiên
next_word()

# Bắt đầu chương trình tkinter
root.mainloop()
