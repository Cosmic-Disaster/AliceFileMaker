# -*- coding: utf-8 -*-
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
from PIL import Image, ImageTk
import re

# ================= 기본 설정 =================
DEFAULT_CONFIG = {
    "PROJECT_ROOT": r"D:/Github/AliceRenderer",
    "TARGET_DIR": r"src",  # 이제 기본 타겟은 src 루트입니다.
    "CMAKE_FILE": r"CMakeLists.txt",
    "CMAKE_VAR_PREFIX": "${ALICE_SRC_DIR}",
    "BG_IMAGE": "background.png"
}
CONFIG_FILE_NAME = "config.json"
# ===========================================

class AliceEngineManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Alice Engine Manager (Tree View)")
        self.root.geometry("1000x800")
        
        # 설정 로드
        self.config = self.load_config()

        # 배경 및 스타일
        self.setup_style()
        self.setup_background()
        
        # UI 구성
        self.setup_ui()
        
        # 트리 초기화
        self.refresh_tree()

    def load_config(self):
        if os.path.exists(CONFIG_FILE_NAME):
            try:
                with open(CONFIG_FILE_NAME, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        self.config["PROJECT_ROOT"] = self.entry_root.get()
        self.config["TARGET_DIR"] = self.entry_target.get()
        self.config["CMAKE_FILE"] = self.entry_cmake.get()
        
        try:
            with open(CONFIG_FILE_NAME, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("저장 완료", "설정이 저장되었습니다.")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("실패", f"저장 실패: {e}")

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2d2d2d", 
                        foreground="white", 
                        fieldbackground="#2d2d2d",
                        font=("Consolas", 10))
        style.map('Treeview', background=[('selected', '#4a4a4a')])

    def setup_background(self):
        bg_path = self.config.get("BG_IMAGE", "background.png")
        try:
            if os.path.exists(bg_path):
                self.bg_img = Image.open(bg_path)
                self.bg_img = self.bg_img.resize((1000, 800), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(self.bg_img)
                self.bg_label = tk.Label(self.root, image=self.bg_photo)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                self.root.configure(bg='#2b2b2b')
        except:
            self.root.configure(bg='#2b2b2b')

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1e1e1e", bd=2)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=900, height=700)

        # --- 상단 설정 ---
        setting_frame = tk.LabelFrame(main_frame, text=" 환경 설정 ", font=("Arial", 10, "bold"), bg="#1e1e1e", fg="white")
        setting_frame.pack(padx=10, pady=5, fill="x")

        # Project Root
        tk.Label(setting_frame, text="프로젝트 루트:", bg="#1e1e1e", fg="#cccccc").grid(row=0, column=0, sticky="e")
        self.entry_root = tk.Entry(setting_frame, width=60)
        self.entry_root.insert(0, self.config["PROJECT_ROOT"])
        self.entry_root.grid(row=0, column=1, padx=5)
        tk.Button(setting_frame, text="찾기", command=self.browse_root, bg="#555", fg="white").grid(row=0, column=2)

        # Src Dir
        tk.Label(setting_frame, text="소스 폴더(src):", bg="#1e1e1e", fg="#cccccc").grid(row=1, column=0, sticky="e")
        self.entry_target = tk.Entry(setting_frame, width=60)
        self.entry_target.insert(0, self.config["TARGET_DIR"])
        self.entry_target.grid(row=1, column=1, padx=5)
        
        # CMake File
        tk.Label(setting_frame, text="CMake 파일명:", bg="#1e1e1e", fg="#cccccc").grid(row=2, column=0, sticky="e")
        self.entry_cmake = tk.Entry(setting_frame, width=60)
        self.entry_cmake.insert(0, self.config["CMAKE_FILE"])
        self.entry_cmake.grid(row=2, column=1, padx=5)

        tk.Button(setting_frame, text="적용 및 저장", bg="#FF9800", fg="black", command=self.save_config).grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        # --- 트리 뷰 영역 ---
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # 스크롤바
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, show="tree headings")
        self.tree.heading("#0", text="Project Structure (src)", anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # --- 하단 버튼 ---
        btn_frame = tk.Frame(main_frame, bg="#1e1e1e")
        btn_frame.pack(pady=15)
        
        btn_opts = {"font": ("Arial", 10, "bold"), "width": 18, "height": 2}
        tk.Button(btn_frame, text="클래스 추가 (.h+.cpp)", bg="#4CAF50", fg="white", command=self.add_class, **btn_opts).pack(side="left", padx=10)
        tk.Button(btn_frame, text="파일 삭제", bg="#f44336", fg="white", command=self.delete_item, **btn_opts).pack(side="left", padx=10)
        tk.Button(btn_frame, text="새로고침", bg="#2196F3", fg="white", command=self.refresh_tree, **btn_opts).pack(side="left", padx=10)

    def browse_root(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_root.delete(0, tk.END)
            self.entry_root.insert(0, path)

    def get_paths(self):
        root_path = self.entry_root.get()
        target_sub = self.entry_target.get()
        cmake_file = self.entry_cmake.get()
        return os.path.join(root_path, target_sub), os.path.join(root_path, cmake_file)

    def refresh_tree(self):
        # 트리 초기화
        self.tree.delete(*self.tree.get_children())
        full_src_path, _ = self.get_paths()

        if not os.path.exists(full_src_path):
            return

        # 루트 노드 추가
        root_node = self.tree.insert("", "end", text="src", open=True, values=(full_src_path,))
        self.process_directory(root_node, full_src_path)

    def process_directory(self, parent_node, path):
        try:
            items = os.listdir(path)
            # 폴더 먼저 정렬, 그 다음 파일
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x))

            for item in items:
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                
                # 아이콘/텍스트 장식
                display_text = f"📁 {item}" if is_dir else f"📄 {item}"
                
                # 노드 삽입
                node = self.tree.insert(parent_node, "end", text=display_text, open=False, values=(full_path, "dir" if is_dir else "file"))
                
                if is_dir:
                    self.process_directory(node, full_path)
        except PermissionError:
            pass

    def get_selected_path_info(self):
        """선택된 항목의 경로와 타입(dir/file) 반환"""
        selected = self.tree.selection()
        if not selected:
            return None, None
        item = self.tree.item(selected[0])
        # values[0]은 full_path, values[1]은 type
        return item['values'][0], item['values'][1]

    def add_class(self):
        # 1. 위치 선정
        path, type_ = self.get_selected_path_info()
        full_src_path, full_cmake_path = self.get_paths()

        if not path:
            target_dir = full_src_path # 선택 안했으면 src 루트
        elif type_ == "file":
            target_dir = os.path.dirname(path) # 파일 선택했으면 그 폴더
        else:
            target_dir = path # 폴더 선택했으면 그 폴더

        # 2. 이름 입력
        class_name = simpledialog.askstring("클래스 생성", "클래스 이름(C++)을 입력하세요:\n(.h와 .cpp가 모두 생성됩니다)")
        if not class_name:
            return

        h_file = f"{class_name}.h"
        cpp_file = f"{class_name}.cpp"
        
        h_full = os.path.join(target_dir, h_file)
        cpp_full = os.path.join(target_dir, cpp_file)

        if os.path.exists(h_full) or os.path.exists(cpp_full):
            messagebox.showwarning("중복", "이미 존재하는 파일입니다.")
            return

        try:
            # 3. 파일 생성 (UTF-8 BOM)
            # Header
            with open(h_full, 'w', encoding='utf-8-sig') as f:
                f.write(f"#pragma once\n\n// {class_name} header\n\nclass {class_name} {{\npublic:\n\t{class_name}();\n\t~{class_name}();\n}};\n")
            
            # Cpp
            with open(cpp_full, 'w', encoding='utf-8-sig') as f:
                f.write(f"#include \"{h_file}\"\n\n{class_name}::{class_name}() {{\n}}\n\n{class_name}::~{class_name}() {{\n}}\n")

            # 4. CMake 업데이트 (두 파일 모두 전달)
            self.update_cmake(full_cmake_path, target_dir, [h_file, cpp_file], mode="add")

            messagebox.showinfo("성공", f"{class_name} 클래스가 생성되었습니다.")
            self.refresh_tree()
            
            # 생성된 폴더 열어주기 (시각적 피드백)
            # (복잡하면 생략 가능, 여기선 리프레시만)

        except Exception as e:
            messagebox.showerror("오류", f"생성 실패: {e}")

    def delete_item(self):
        path, type_ = self.get_selected_path_info()
        if not path:
            messagebox.showwarning("선택", "삭제할 항목을 선택해주세요.")
            return

        if type_ == "dir":
            messagebox.showwarning("주의", "폴더 삭제는 파일 탐색기에서 직접 해주세요.\n(CMake 꼬임 방지)")
            return

        filename = os.path.basename(path)
        if not messagebox.askyesno("확인", f"정말 {filename} 파일을 삭제하시겠습니까?"):
            return

        _, full_cmake_path = self.get_paths()
        target_dir = os.path.dirname(path)

        try:
            os.remove(path)
            self.update_cmake(full_cmake_path, target_dir, [filename], mode="delete")
            messagebox.showinfo("성공", "삭제되었습니다.")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("오류", f"삭제 실패: {e}")

    def update_cmake(self, cmake_path, file_dir, filenames, mode="add"):
        """
        파일을 CMakeLists.txt의 ENGINE_SOURCES 혹은 ENGINE_HEADERS에 추가/삭제
        """
        if not os.path.exists(cmake_path):
            raise FileNotFoundError("CMakeLists.txt 없음")

        # 1. 상대 경로 계산 (${ALICE_SRC_DIR}/Core/File.h 형식 만들기 위함)
        # config['TARGET_DIR'] (보통 src) 로부터의 상대 경로
        root_path = self.entry_root.get()
        src_root = os.path.join(root_path, self.config["TARGET_DIR"]) # D:/.../src
        
        # file_dir이 src_root의 하위라고 가정
        try:
            rel_dir = os.path.relpath(file_dir, src_root) # Core/Component 등
        except ValueError:
            rel_dir = "" # src 루트인 경우

        # 윈도우 경로 구분자 변경
        rel_dir = rel_dir.replace("\\", "/")
        if rel_dir == ".": rel_dir = ""

        # 접두어 (/${ALICE_SRC_DIR})
        prefix = self.config.get("CMAKE_VAR_PREFIX", "${ALICE_SRC_DIR}")
        
        # 경로 조합 함수
        def make_cmake_path(fname):
            if rel_dir:
                return f"{prefix}/{rel_dir}/{fname}"
            else:
                return f"{prefix}/{fname}"

        with open(cmake_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 2. 내용 수정
        new_lines = []
        
        if mode == "delete":
            # 삭제는 단순함: 해당 문자열이 포함된 줄을 제거
            targets = [make_cmake_path(f) for f in filenames]
            for line in lines:
                skip = False
                for t in targets:
                    # 경로 구분자 통일 후 비교
                    if t in line.replace("\\", "/"):
                        skip = True
                        break
                if not skip:
                    new_lines.append(line)
        
        elif mode == "add":
            # 추가는 똑똑하게 해야 함 (.cpp는 SOURCES에, .h는 HEADERS에)
            # 상태 머신 사용
            in_sources = False
            in_headers = False
            
            # 추가해야 할 파일들 분류
            to_add_sources = [make_cmake_path(f) for f in filenames if f.endswith('.cpp') or f.endswith('.c')]
            to_add_headers = [make_cmake_path(f) for f in filenames if f.endswith('.h') or f.endswith('.hpp')]
            
            added_sources = False
            added_headers = False

            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # 블록 시작 감지
                if "set(ENGINE_SOURCES" in line:
                    in_sources = True
                elif "set(ENGINE_HEADERS" in line:
                    in_headers = True
                
                # 블록 끝 감지 (닫는 괄호)
                # 주의: 괄호가 같은 줄에 있을 수도, 다른 줄에 있을 수도 있음.
                # 제공된 CMake는 닫는 괄호가 보통 단독 줄 혹은 들여쓰기 뒤에 있음.
                
                if in_sources:
                    # 블록이 끝나는 지점인가? (보통 ')' 하나만 있거나 주석 뒤에 있음)
                    if stripped.startswith(")"):
                        # 여기서 소스 파일 추가
                        if not added_sources and to_add_sources:
                            # 1. 같은 폴더(rel_dir)에 있는 파일이 이미 리스트에 있는지 찾아보고 그 뒤에 넣기 (그룹핑)
                            insert_idx = len(new_lines) # 기본: 닫는 괄호 바로 앞
                            
                            # (선택사항: 정교한 위치 찾기는 복잡하므로, 그냥 마지막에 추가하되 
                            #  가능하면 해당 폴더 주석이 보이면 좋겠지만 여기선 맨 뒤 추가)
                            for path_str in to_add_sources:
                                new_lines.append(f"\t{path_str}\n")
                            
                            added_sources = True
                        in_sources = False
                
                if in_headers:
                    if stripped.startswith(")"):
                        if not added_headers and to_add_headers:
                            for path_str in to_add_headers:
                                new_lines.append(f"\t{path_str}\n")
                            added_headers = True
                        in_headers = False

                new_lines.append(line)

            # 만약 블록을 못 찾았거나 파일을 못 넣었으면 (예외처리)
            if to_add_sources and not added_sources:
                print("경고: ENGINE_SOURCES 블록을 찾지 못했습니다.")
            if to_add_headers and not added_headers:
                print("경고: ENGINE_HEADERS 블록을 찾지 못했습니다.")

        with open(cmake_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

if __name__ == "__main__":
    root = tk.Tk()
    app = AliceEngineManager(root)
    root.mainloop()