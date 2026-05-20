"""Reusable confirmation dialog for destructive actions — luxury styling."""

import customtkinter as ctk

from theme.colors import ACCENT_ERROR, BG_DARK, BG_LIGHT, BORDER, CARD_RADIUS, PRIMARY, PRIMARY_HOVER, TEXT_PRIMARY, TEXT_SECONDARY


class ConfirmActionDialog(ctk.CTkToplevel):
    """Reusable confirmation dialog for destructive actions."""

    def __init__(self, master, title: str, message: str, confirm_text: str, confirm_color: str, on_confirm):
        super().__init__(master)
        self.on_confirm = on_confirm
        self.title(title)
        self.geometry("440x260")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=21, weight="bold", family="Helvetica"),
            text_color=TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w", padx=28, pady=(28, 8))

        message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14, family="Helvetica"),
            text_color=TEXT_SECONDARY,
            wraplength=380,
            justify="left"
        )
        message_label.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 24))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=28, pady=(12, 28))
        actions.grid_columnconfigure((0, 1), weight=1)

        cancel = ctk.CTkButton(
            actions,
            text="Cancel",
            height=40,
            fg_color=BG_LIGHT,
            hover_color=BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self.destroy
        )
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        confirm = ctk.CTkButton(
            actions,
            text=confirm_text,
            height=40,
            fg_color=confirm_color,
            hover_color="#C62828" if confirm_color == ACCENT_ERROR else confirm_color,
            text_color=BG_DARK,
            font=ctk.CTkFont(size=12, weight="bold", family="Helvetica"),
            corner_radius=CARD_RADIUS,
            command=self._confirm
        )
        confirm.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _confirm(self):
        self.destroy()
        self.on_confirm()
