import tkinter as tk
import random
import pdfplumber
import os
from googletrans import Translator  # Thư viện để dịch tự động

# Đường dẫn tới các file lưu từ
correct_words_file = "words_correct.txt"
wrong_words_file = "words_wrong.txt"

# Khởi tạo Google Translator
translator = Translator()

# Hàm trích xuất từ từ file PDF
def extract_words_from_pdf(pdf_path):
    words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                words += text.split()  # Chia nhỏ các từ ra
    return list(set(words))  # Loại bỏ từ trùng lặp

# Hàm dịch từ sang tiếng Việt
def translate_word(word):
    try:
        translation = translator.translate(word, src='en', dest='vi')
        return translation.text.strip()  # Loại bỏ khoảng trắng thừa
    except Exception as e:
        return word.strip()  # Nếu không dịch được, trả về từ gốc và loại bỏ khoảng trắng thừa

# Hàm lưu từ vào file txt
def log_word(word, file_path):
    with open(file_path, "a") as file:
        file.write(f"{word.strip()}\n")  # Loại bỏ khoảng trắng thừa khi lưu

# Hàm xóa từ khỏi file txt
def remove_word_from_file(word, file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            words = [line.strip() for line in file.readlines()]
        if word in words:
            words.remove(word)
        with open(file_path, "w") as file:
            for w in words:
                file.write(f"{w.strip()}\n")

# Hàm kiểm tra đáp án và lưu kết quả
def check_answer(selected_option):
    global current_question
    correct_word, correct_meaning, options = current_question  # Lấy nghĩa đã dịch từ câu hỏi
    
    # So sánh nghĩa tiếng Việt đã dịch và đáp án người dùng chọn
    if selected_option == correct_meaning:  # So sánh trực tiếp giữa nghĩa đã dịch và lựa chọn của người dùng
        result_label.config(text="Đúng!")
        log_word(correct_word, correct_words_file)  # Lưu từ vào file đúng
    else:
        result_label.config(text=f"Sai! Đáp án đúng là: {correct_meaning}")
        log_word(correct_word, wrong_words_file)  # Lưu từ vào file sai
    root.after(2000, next_question)

# Chuyển sang câu hỏi tiếp theo
def next_question():
    global current_question
    current_question = create_flashcard_question(word_list)
    correct_word, correct_meaning, options = current_question
    
    # Hiển thị câu hỏi từ tiếng Anh và các đáp án nghĩa tiếng Việt
    question_label.config(text=f"Từ: {correct_word}")
    btn_a.config(text=f"A. {options[0]}")
    btn_b.config(text=f"B. {options[1]}")
    btn_c.config(text=f"C. {options[2]}")
    btn_d.config(text=f"D. {options[3]}")
    result_label.config(text="")

# Hàm tạo flashcard câu hỏi
def create_flashcard_question(word_list):
    correct_word = random.choice(word_list)
    correct_meaning = translate_word(correct_word)  # Dịch từ đúng sang tiếng Việt

    options = [correct_meaning]

    # Lấy 3 từ sai ngẫu nhiên và dịch chúng sang tiếng Việt
    while len(options) < 4:
        option = random.choice(word_list)
        translated_option = translate_word(option)
        if translated_option not in options:
            options.append(translated_option)
    
    random.shuffle(options)  # Xáo trộn các lựa chọn
    return correct_word, correct_meaning, options  # Trả về từ gốc, nghĩa đúng và các lựa chọn

# Chuyển từ đã học sang file chưa thuộc và ngược lại
def move_word_between_files(source_file, destination_file):
    global current_question
    correct_word, _, _ = current_question
    # Xóa từ từ file nguồn
    remove_word_from_file(correct_word, source_file)
    # Thêm từ vào file đích
    log_word(correct_word, destination_file)
    result_label.config(text=f"Đã chuyển từ: {correct_word}")
    root.after(2000, next_question)

# Học từ từ file đúng hoặc sai
def study_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            words = [line.strip() for line in file.readlines()]
        if words:
            global word_list
            word_list = words  # Cập nhật danh sách từ hiện tại
            next_question()
        else:
            result_label.config(text="Không có từ nào trong danh sách.")
    else:
        result_label.config(text="Không tìm thấy file.")

# Đường dẫn tới file PDF
pdf_path = 'American_Oxford_3000.pdf'

# Trích xuất danh sách từ từ file PDF
word_list = extract_words_from_pdf(pdf_path)

# Tạo giao diện tkinter
root = tk.Tk()
root.title("Flashcard Học Từ Vựng")

question_label = tk.Label(root, text="", font=('Arial', 16), wraplength=400)
question_label.pack(pady=20)

btn_a = tk.Button(root, text="", font=('Arial', 14), width=40, command=lambda: check_answer(btn_a.cget("text")))
btn_a.pack(pady=5)

btn_b = tk.Button(root, text="", font=('Arial', 14), width=40, command=lambda: check_answer(btn_b.cget("text")))
btn_b.pack(pady=5)

btn_c = tk.Button(root, text="", font=('Arial', 14), width=40, command=lambda: check_answer(btn_c.cget("text")))
btn_c.pack(pady=5)

btn_d = tk.Button(root, text="", font=('Arial', 14), width=40, command=lambda: check_answer(btn_d.cget("text")))
btn_d.pack(pady=5)

result_label = tk.Label(root, text="", font=('Arial', 14))
result_label.pack(pady=20)

# Nút chuyển từ đã học sang file chưa thuộc
btn_move_to_wrong = tk.Button(root, text="Chuyển sang chưa học", font=('Arial', 14), command=lambda: move_word_between_files(correct_words_file, wrong_words_file))
btn_move_to_wrong.pack(pady=10)

# Nút chuyển từ chưa thuộc sang đã học
btn_move_to_correct = tk.Button(root, text="Chuyển sang đã học", font=('Arial', 14), command=lambda: move_word_between_files(wrong_words_file, correct_words_file))
btn_move_to_correct.pack(pady=10)

# Nút để học từ file đúng
btn_study_correct = tk.Button(root, text="Học từ file đã đúng", font=('Arial', 14), command=lambda: study_from_file(correct_words_file))
btn_study_correct.pack(pady=10)

# Nút để học từ file sai
btn_study_wrong = tk.Button(root, text="Học từ file sai", font=('Arial', 14), command=lambda: study_from_file(wrong_words_file))
btn_study_wrong.pack(pady=10)

next_question()  # Khởi tạo câu hỏi đầu tiên

# Bắt đầu chương trình tkinter
root.mainloop()
