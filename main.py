import google.generativeai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext, font
import tkinter.font as tkfont
from ttkthemes import ThemedTk

# Configure Gemini API
GOOGLE_API_KEY = 'AIzaSyBIKZZOcguAIorOML1OTQF9O9O5bniToMI'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

class AICalculator:
    def __init__(self):
        self.window = ThemedTk(theme="arc")  # Modern, clean theme
        self.window.title("CalcGPT - Your Mathematical Assistant")
        self.window.geometry("800x900")
        self.window.configure(bg='#f0f0f0')  # Light gray background
        
        # Configure fonts
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.window.option_add("*Font", default_font)
        
        # Title Label with gradient effect
        title_frame = tk.Frame(self.window, bg='#2c3e50')
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew")
        title_label = tk.Label(
            title_frame,
            text="CalcGPT",
            font=("Helvetica", 24, "bold"),
            fg='white',
            bg='#2c3e50',
            pady=10
        )
        title_label.pack()
        
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="20 10 20 10")
        main_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        
        # Standard Calculator Display with modern font
        self.display = ttk.Entry(
            main_frame,
            justify="right",
            font=("Consolas", 24),
            style="Large.TEntry"
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=5, pady=15, sticky="nsew")
        
        # Loading indicator with animation
        self.loading_label = ttk.Label(
            main_frame,
            text="",
            font=("Helvetica", 12),
            style="Info.TLabel"
        )
        self.loading_label.grid(row=1, column=0, columnspan=4, padx=5, sticky="nsew")
        
        # AI Chat Display with better formatting
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            height=12,
            font=("Consolas", 12),
            wrap=tk.WORD,
            bg='#ffffff',
            fg='#2c3e50'
        )
        self.chat_display.grid(row=2, column=0, columnspan=4, padx=5, pady=15, sticky="nsew")
        
        # Configure tag for formatting math expressions
        self.chat_display.tag_configure("math", font=("Consolas", 12, "bold"), foreground="#1a73e8")
        
        # Button styles
        style = ttk.Style()
        style.configure(
            "Calculator.TButton",
            padding=10,
            font=("Helvetica", 14),
            width=8
        )
        style.configure(
            "Operation.TButton",
            padding=10,
            font=("Helvetica", 14, "bold"),
            width=8
        )
        style.configure(
            "Special.TButton",
            padding=10,
            font=("Helvetica", 14, "bold"),
            width=16
        )
        
        # Calculator Buttons with modern design
        buttons = [
            ('7', 'Calculator'), ('8', 'Calculator'), ('9', 'Calculator'), ('/', 'Operation'),
            ('4', 'Calculator'), ('5', 'Calculator'), ('6', 'Calculator'), ('*', 'Operation'),
            ('1', 'Calculator'), ('2', 'Calculator'), ('3', 'Calculator'), ('-', 'Operation'),
            ('0', 'Calculator'), ('.', 'Calculator'), ('=', 'Operation'), ('+', 'Operation')
        ]
        
        button_frame = ttk.Frame(main_frame, padding="5 15 5 5")
        button_frame.grid(row=3, column=0, columnspan=4, sticky="nsew")
        
        row = 0
        col = 0
        for (button, style_name) in buttons:
            cmd = lambda x=button: self.click(x)
            ttk.Button(
                button_frame,
                text=button,
                command=cmd,
                style=f"{style_name}.TButton"
            ).grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Action buttons with distinct styling
        action_frame = ttk.Frame(main_frame, padding="5 15 5 15")
        action_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        
        ttk.Button(
            action_frame,
            text="Clear All",
            command=self.clear,
            style="Special.TButton"
        ).grid(row=0, column=0, columnspan=2, padx=4, pady=4, sticky="nsew")
        
        ttk.Button(
            action_frame,
            text="Ask AI Help",
            command=self.ai_help,
            style="Special.TButton"
        ).grid(row=0, column=2, columnspan=2, padx=4, pady=4, sticky="nsew")
        
        # Configure grid weights
        for i in range(4):
            self.window.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.window.grid_rowconfigure(i, weight=1)

    def click(self, key):
        if key == '=':
            try:
                expression = self.display.get()
                result = eval(expression)
                print(f"\n📥 Input: {expression}")
                print(f"📤 Result: {result}\n")
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, str(result))
            except:
                self.display.delete(0, tk.END)
                self.display.insert(tk.END, "Error")
                print("\n❌ Error: Invalid expression\n")
        else:
            self.display.insert(tk.END, key)

    def clear(self):
        self.display.delete(0, tk.END)
        self.chat_display.delete(1.0, tk.END)

    def show_loading(self, show=True):
        if show:
            self.loading_label.config(
                text="🧮 Calculating...",
                foreground="#1a73e8",  # Google Blue
                background="#e8f0fe"   # Light blue background
            )
        else:
            self.loading_label.config(text="")
        self.window.update()

    def ai_help(self):
        # Get the current expression
        expression = self.display.get()
        if not expression:
            return
        
        self.show_loading(True)
        
        # Generate response using Gemini
        system_prompt = """You are CalcGPT, a friendly calculator that gives quick, concise answers.
        Keep responses under 4 short paragraphs total.
        Use simple language and be encouraging but brief.
        Format: Quick greeting -> Result -> Brief explanation -> Short tip/encouragement
        """
        
        user_prompt = f"""Expression: {expression}
        Give me a quick analysis with:
        - The result
        - A simple explanation in 2-3 sentences
        - One quick helpful tip
        Be concise and friendly!
        """
        
        try:
            print("\n" + "="*50)
            print(f"📝 Question: {expression}")
            print("="*50)
            
            # Combine prompts into one
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = model.generate_content(combined_prompt)
            
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.insert(tk.END, response.text)
            
            print(f"\n🤖 CalcGPT Response:")
            print("-"*50)
            print(response.text)
            print("="*50 + "\n")
        except Exception as e:
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.insert(tk.END, f"❌ Oops! Something went wrong:\n{str(e)}\n\nTry another calculation!")
        finally:
            self.show_loading(False)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calculator = AICalculator()
    calculator.run()
