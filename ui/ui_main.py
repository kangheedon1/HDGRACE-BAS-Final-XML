#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDGRACE UI 메인 모듈
사용자 인터페이스 초기화 및 상호작용 관리
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from datetime import datetime

class HDGRACEMainUI:
    """HDGRACE 메인 UI 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HDGRACE BAS 29.3.1 Commercial System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성 요소 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 타이틀
        title_label = ttk.Label(
            main_frame, 
            text="🚀 HDGRACE BAS 29.3.1 Commercial XML Generator",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # 제어 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.generate_btn = ttk.Button(
            button_frame,
            text="▶️ XML 생성 시작",
            command=self.start_generation,
            width=20
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ 중지",
            command=self.stop_generation,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 진행률 표시
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=600
        )
        self.progress.pack(pady=10)
        
        # 로그 텍스트 영역
        log_frame = ttk.LabelFrame(main_frame, text="실행 로그", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(
            log_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 상태 바
        self.status_var = tk.StringVar()
        self.status_var.set("대기 중...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_generation(self):
        """XML 생성 시작"""
        self.generate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.status_var.set("XML 생성 중...")
        
        self.log_message("🚀 HDGRACE XML 생성 시작")
        
        # 별도 스레드에서 생성 실행
        self.generation_thread = threading.Thread(target=self.run_generation)
        self.generation_thread.daemon = True
        self.generation_thread.start()
        
    def run_generation(self):
        """XML 생성 실행"""
        try:
            from c import main as c_main
            result = c_main()
            
            if result:
                self.log_message("✅ XML 생성 완료!")
                messagebox.showinfo("성공", "XML 생성이 완료되었습니다!")
            else:
                self.log_message("❌ XML 생성 실패!")
                messagebox.showerror("실패", "XML 생성 중 오류가 발생했습니다.")
                
        except Exception as e:
            self.log_message(f"❌ 오류 발생: {e}")
            messagebox.showerror("오류", f"생성 중 오류가 발생했습니다: {e}")
        finally:
            self.root.after(0, self.generation_complete)
            
    def generation_complete(self):
        """생성 완료 후 UI 상태 복원"""
        self.progress.stop()
        self.generate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("완료")
        
    def stop_generation(self):
        """생성 중지"""
        self.log_message("⏹️ 생성 중지 요청")
        self.generation_complete()
        
    def run(self):
        """UI 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = HDGRACEMainUI()
    app.run()
