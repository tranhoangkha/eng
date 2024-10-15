import tkinter as tk
import random
import pdfplumber
import os
import re  # Để làm sạch các ký tự thừa
from googletrans import Translator  # Thư viện để dịch tự động
import unicodedata

# Đường dẫn tới các file lưu từ
correct_words_file = "words_correct.txt"
wrong_words_file = "words_wrong.txt"

# Khởi tạo Google Translator
translator = Translator()
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Hàm trích xuất từ từ file PDF
def extract_words_from_pdf(pdf_path):
    words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                words += re.findall(r'\b\w+\b', text)  # Chỉ lấy từ, bỏ các ký tự đặc biệt
    return list(set(words))  # Loại bỏ từ trùng lặp

# Hàm dịch từ sang tiếng Việt
def translate_word(word):
    cleaned_word = clean_word(word)  # Làm sạch từ trước khi dịch
    if not cleaned_word.isalpha():  # Kiểm tra nếu từ chứa ký tự không phải chữ cái
        return f"Từ không hợp lệ: {cleaned_word}"  # Thông báo lỗi cho từ không hợp lệ
    try:
        translation = translator.translate(cleaned_word, src='en', dest='vi')
        return translation.text.strip()  # Loại bỏ khoảng trắng thừa
    except Exception as e:
        return cleaned_word.strip()

# Hàm lưu từ vào file txt
# Hàm lưu từ vào file txt nếu từ chưa tồn tại
def log_word(word, file_path):
    # Kiểm tra nếu file tồn tại và từ chưa có trong file
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            words = [line.strip() for line in file.readlines()]
            if word in words:
                return  # Nếu từ đã tồn tại thì không lưu
    # Lưu từ vào file nếu chưa có
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

# Cập nhật hàm làm sạch từ, bỏ các ký tự không phải chữ cái (kể cả số)
def clean_word(word):
    return re.sub(r'[^a-zA-Z]', '', word).strip()


# Hàm kiểm tra đáp án và lưu kết quả
def check_answer(selected_option):
    global current_question
    correct_word, correct_meaning, options = current_question  # Lấy nghĩa đã dịch từ câu hỏi
    
    # Tách bỏ "A. ", "B. ", "C. ", "D. " để chỉ lấy phần nghĩa
    selected_option_meaning = selected_option.split(". ", 1)[1]  # Chỉ lấy phần sau "A. ", "B. "...    

    # Làm sạch nghĩa để tránh các lỗi về dấu chấm, dấu phẩy
    selected_option_meaning = clean_word(selected_option_meaning)
    correct_meaning = clean_word(correct_meaning)

    # So sánh nghĩa tiếng Việt đã dịch và đáp án người dùng chọn
    if selected_option_meaning == correct_meaning:  # So sánh trực tiếp giữa nghĩa đã dịch và lựa chọn của người dùng
        result_label.config(text="Đúng!", bg='#d3f8e2')
        log_word(correct_word, correct_words_file)  # Lưu từ vào file đúng
    else:
        correct_meaning_no_accents = remove_accents(correct_meaning)
        result_label.config(text=f"Sai! Đáp án đúng là: {correct_meaning_no_accents}", bg='#f8d7da', font=('Arial', 12))

        # result_label.config(text=f"Sai! Đáp án đúng là: {correct_meaning}", bg='#f8d7da')

        log_word(correct_word, wrong_words_file)  # Lưu từ vào file sai
    
    update_stt_labels()  # Cập nhật số thứ tự của cả hai file
    start_timer(0.1, next_question)  # Đợi 0.5 giây và chuyển sang câu hỏi tiếp theo

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
    timer_label.config(text="")  # Reset bộ đếm thời gian

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

# Đếm ngược thời gian và hiển thị lên màn hình
def start_timer(duration, callback):
    remaining_time = duration

    def update_timer():
        nonlocal remaining_time
        if remaining_time > 0:
            timer_label.config(text=f"Chờ: {remaining_time:.1f} giây")
            remaining_time -= 0.1
            root.after(100, update_timer)
        else:
            callback()

    update_timer()

# Chuyển từ đã học sang file chưa thuộc và ngược lại
def move_word_between_files(source_file, destination_file):
    global current_question
    correct_word, _, _ = current_question
    # Xóa từ từ file nguồn
    remove_word_from_file(correct_word, source_file)
    # Thêm từ vào file đích
    log_word(correct_word, destination_file)
    result_label.config(text=f"Đã chuyển từ: {correct_word}")
    update_stt_labels()  # Cập nhật số từ (STT)
    start_timer(0.5, next_question)  # Đợi 0.5 giây và chuyển sang câu hỏi tiếp theo

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

# Cập nhật số thứ tự (STT) của file đúng và file sai
def update_stt_labels():
    correct_count = count_words_in_file(correct_words_file)
    wrong_count = count_words_in_file(wrong_words_file)
    stt_correct_label.config(text=f"STT đúng: {correct_count}")
    stt_wrong_label.config(text=f"STT sai: {wrong_count}")

# Hàm đếm số từ trong file
def count_words_in_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return len([line.strip() for line in file.readlines()])
    return 0

# Đường dẫn tới file PDF
pdf_path = 'American_Oxford_3000.pdf'

# Trích xuất danh sách từ từ file PDF
word_list = extract_words_from_pdf(pdf_path)

# Tạo giao diện tkinter
root = tk.Tk()
root.title("Flashcard Học Từ Vựng")

question_label = tk.Label(root, text="", font=('Arial', 16), wraplength=400)
question_label.pack(pady=20)

timer_label = tk.Label(root, text="", font=('Arial', 14))  # Hiển thị bộ đếm thời gian
timer_label.pack(pady=10)

# Chỉnh lại các nút để bỏ border nhưng vẫn giữ giao diện mặc định
btn_a = tk.Button(root, text="", font=('Arial', 12), width=30, command=lambda: check_answer(btn_a.cget("text")),
                  highlightthickness=0, bd=0)  # Bỏ viền đen
btn_a.pack(pady=5)

btn_b = tk.Button(root, text="", font=('Arial', 12), width=30, command=lambda: check_answer(btn_b.cget("text")),
                  highlightthickness=0, bd=0)  # Bỏ viền đen
btn_b.pack(pady=5)

btn_c = tk.Button(root, text="", font=('Arial', 12), width=30, command=lambda: check_answer(btn_c.cget("text")),
                  highlightthickness=0, bd=0)  # Bỏ viền đen
btn_c.pack(pady=5)

btn_d = tk.Button(root, text="", font=('Arial', 12), width=30, command=lambda: check_answer(btn_d.cget("text")),
                  highlightthickness=0, bd=0)  # Bỏ viền đen
btn_d.pack(pady=5)

result_label = tk.Label(root, text="", font=('Arial', 14))
result_label.pack(pady=20)

# Nút chuyển từ đã học sang file chưa thuộc
btn_move_to_wrong = tk.Button(root, text="Chuyển sang chưa học", font=('Arial', 12), command=lambda: move_word_between_files(correct_words_file, wrong_words_file))
btn_move_to_wrong.pack(pady=10)

# Hiển thị số thứ tự file sai
stt_wrong_label = tk.Label(root, text=f"STT sai: {count_words_in_file(wrong_words_file)}", font=('Arial', 12))
stt_wrong_label.pack(pady=5)


# Nút chuyển từ chưa thuộc sang đã học
btn_move_to_correct = tk.Button(root, text="Chuyển sang đã học", font=('Arial', 12), command=lambda: move_word_between_files(wrong_words_file, correct_words_file))
btn_move_to_correct.pack(pady=10)
# Hiển thị số thứ tự file đúng
stt_correct_label = tk.Label(root, text=f"STT đúng: {count_words_in_file(correct_words_file)}", font=('Arial', 12))
stt_correct_label.pack(pady=5)

# Nút để học từ file đã đúng
btn_study_correct = tk.Button(root, text="Học từ file đã đúng", font=('Arial', 12), command=lambda: study_from_file(correct_words_file))
btn_study_correct.pack(pady=10)

# Nút để học từ file sai
btn_study_wrong = tk.Button(root, text="Học từ file sai", font=('Arial', 12), command=lambda: study_from_file(wrong_words_file))
btn_study_wrong.pack(pady=10)

# Bắt đầu với câu hỏi đầu tiên
next_question()

# Khởi động cập nhật STT khi khởi động chương trình
update_stt_labels()

# Bắt đầu chương trình tkinter
root.mainloop()
