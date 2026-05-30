"""
giao_dien_server.py
Giao diện desktop Tkinter cho server.
Nhiệm vụ chính:
- hiển thị danh sách các khu
- xem ảnh mới nhất của từng khu
- thêm khu, xóa khu
- xem lịch sử và cài đặt của từng khu
- tự động làm mới dữ liệu từ Flask API
"""

import io

import cv2
import numpy as np
import requests
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, ttk


REFRESH_MS = 700
CARD_IMAGE_WIDTH = 360
CARD_IMAGE_HEIGHT = 220
SERVER_BASE_URL = "http://127.0.0.1:5000"
HISTORY_IMAGE_WIDTH = 380
HISTORY_IMAGE_HEIGHT = 250


class TheKhu:
    """Thẻ giao diện đại diện cho một khu trên màn hình giám sát."""

    def __init__(self, parent, zone_id, delete_callback, settings_callback, history_callback):
        self.zone_id = zone_id
        self.delete_callback = delete_callback
        self.settings_callback = settings_callback
        self.history_callback = history_callback
        self.photo = None
        self.last_time = None
        self.last_detections = None
        self.last_client = None

        self.frame = tk.Frame(parent, bd=1, relief="solid", bg="white", padx=10, pady=10)

        header = tk.Frame(self.frame, bg="white")
        header.pack(fill="x")

        self.title_label = tk.Label(header, text="", font=("Arial", 12, "bold"), bg="white")
        self.title_label.pack(side="left", anchor="w")

        self.status_label = tk.Label(header, text="", font=("Arial", 10, "bold"), bg="white")
        self.status_label.pack(side="left", padx=10)

        button_group = tk.Frame(header, bg="white")
        button_group.pack(side="right")

        self.history_button = tk.Button(
            button_group,
            text="Lịch sử",
            command=lambda: self.history_callback(self.zone_id)
        )
        self.history_button.pack(side="left", padx=(0, 4))

        self.settings_button = tk.Button(
            button_group,
            text="Cài đặt",
            command=lambda: self.settings_callback(self.zone_id)
        )
        self.settings_button.pack(side="left", padx=(0, 4))

        self.delete_button = tk.Button(
            button_group,
            text="Xóa",
            bg="#d32f2f",
            fg="white",
            command=lambda: self.delete_callback(self.zone_id)
        )
        self.delete_button.pack(side="left")

        self.image_label = tk.Label(self.frame, bg="black")
        self.image_label.pack(fill="x", pady=8)

        self.info_label = tk.Label(
            self.frame,
            text="",
            justify="left",
            anchor="w",
            bg="white",
            fg="#333333",
            font=("Consolas", 10)
        )
        self.info_label.pack(fill="x")

    def grid(self, row, column):
        self.frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

    def destroy(self):
        self.frame.destroy()

    def can_update_frame(self, zone_info):
        return (
            self.last_time != zone_info.get("time")
            or self.last_detections != zone_info.get("detections")
            or self.last_client != zone_info.get("client_id")
        )

    def update(self, zone_info, frame=None):
        self.title_label.config(text=zone_info["name"])

        if zone_info["occupied"]:
            self.status_label.config(text="Đang có client", fg="#b71c1c")
        else:
            self.status_label.config(text="Trống", fg="#1b5e20")

        info_text = (
            f"Client: {zone_info['client_id'] or 'Không có'}\n"
            f"Thời gian: {zone_info['time'] or 'Chưa có'}\n"
            f"Kích thước: {zone_info['width']}x{zone_info['height']}\n"
            f"Phát hiện: {zone_info['detections']}\n"
            f"Ngưỡng AI: {zone_info.get('conf_threshold', 0.25):.2f}\n"
            f"Thời gian cảnh báo/lưu lịch sử: {zone_info.get('history_interval', 5)} giây"
        )
        self.info_label.config(text=info_text)

        if frame is not None:
            frame_resized = cv2.resize(frame, (CARD_IMAGE_WIDTH, CARD_IMAGE_HEIGHT))
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=image)
            self.photo = photo
            self.image_label.config(image=photo)

        self.last_time = zone_info.get("time")
        self.last_detections = zone_info.get("detections")
        self.last_client = zone_info.get("client_id")


class CuaSoCaiDatKhu(tk.Toplevel):
    def __init__(self, parent, zone, on_save):
        super().__init__(parent)
        self.title(f"Cài đặt khu - {zone['name']}")
        self.geometry("360x190")
        self.resizable(False, False)
        self.on_save = on_save
        self.zone = zone

        khung = tk.Frame(self, padx=14, pady=14)
        khung.pack(fill="both", expand=True)

        tk.Label(khung, text=f"Tên khu: {zone['name']}", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))

        tk.Label(khung, text="Ngưỡng AI (0.05 - 0.95):").pack(anchor="w")
        self.nguong_var = tk.StringVar(value=str(zone.get("conf_threshold", 0.25)))
        tk.Entry(khung, textvariable=self.nguong_var).pack(fill="x", pady=(0, 10))

        tk.Label(khung, text="Thời gian cảnh báo và lưu lịch sử (giây):").pack(anchor="w")
        self.lich_su_var = tk.StringVar(value=str(zone.get("history_interval", 5)))
        tk.Entry(khung, textvariable=self.lich_su_var).pack(fill="x", pady=(0, 12))

        khung_nut = tk.Frame(khung)
        khung_nut.pack(fill="x", pady=(8, 0))

        tk.Button(khung_nut, text="Lưu", command=self.luu).pack(side="right")
        tk.Button(khung_nut, text="Đóng", command=self.destroy).pack(side="right", padx=(0, 8))

        self.transient(parent)
        self.grab_set()
        self.focus_force()

    def luu(self):
        try:
            du_lieu = {
                "conf_threshold": float(self.nguong_var.get().strip()),
                "history_interval": int(float(self.lich_su_var.get().strip()))
            }
            self.on_save(du_lieu)
            self.destroy()
        except Exception as error:
            messagebox.showerror("Lỗi", str(error), parent=self)


class CuaSoLichSuKhu(tk.Toplevel):
    def __init__(self, parent, zone_id, zone_name, api_get, api_delete):
        super().__init__(parent)
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.api_get = api_get
        self.api_delete = api_delete
        self.title(f"Lịch sử khu - {zone_name}")
        self.geometry("1100x620")

        self.history_data = []
        self.history_images = {}
        self.current_photo = None

        top = tk.Frame(self, padx=10, pady=10)
        top.pack(fill="x")

        tk.Label(top, text=f"LỊCH SỬ KHU: {zone_name}", font=("Arial", 13, "bold")).pack(side="left")
        tk.Button(top, text="Xóa lịch sử", command=self.xoa_lich_su).pack(side="right")
        tk.Button(top, text="Làm mới", command=self.tai_lai).pack(side="right", padx=(0, 8))

        body = tk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        trai = tk.Frame(body)
        trai.pack(side="left", fill="both", expand=True)

        phai = tk.Frame(body, width=420)
        phai.pack(side="right", fill="y", padx=(10, 0))
        phai.pack_propagate(False)

        cot = ("time", "type", "message")
        self.tree = ttk.Treeview(trai, columns=cot, show="headings", height=20)
        self.tree.heading("time", text="Thời gian")
        self.tree.heading("type", text="Loại")
        self.tree.heading("message", text="Nội dung")
        self.tree.column("time", width=150, anchor="w")
        self.tree.column("type", width=110, anchor="w")
        self.tree.column("message", width=430, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(trai, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_history)

        tk.Label(phai, text="Ảnh minh chứng", font=("Arial", 12, "bold")).pack(anchor="w")
        self.image_label = tk.Label(phai, bg="black", width=HISTORY_IMAGE_WIDTH, height=HISTORY_IMAGE_HEIGHT)
        self.image_label.pack(fill="x", pady=(8, 10))

        self.detail_text = tk.Text(phai, wrap="word", font=("Consolas", 10), height=18)
        self.detail_text.pack(fill="both", expand=True)
        self.detail_text.config(state="disabled")

        self.tai_lai()

    def set_detail(self, text):
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")

    def tai_anh_url(self, duong_dan):
        if not duong_dan:
            return None
        try:
            response = self.api_get(duong_dan, timeout=6)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            image.thumbnail((HISTORY_IMAGE_WIDTH, HISTORY_IMAGE_HEIGHT))
            return ImageTk.PhotoImage(image=image)
        except Exception:
            return None

    def tai_lai(self):
        try:
            response = self.api_get(f"/api/zones/{self.zone_id}/history?limit=100", timeout=6)
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không tải được lịch sử khu."))

            self.history_data = data.get("history", [])
            self.history_images = {}

            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, muc in enumerate(self.history_data):
                self.tree.insert("", "end", iid=str(index), values=(
                    muc.get("time", ""),
                    muc.get("type", ""),
                    muc.get("message", "")
                ))

            self.image_label.config(image="")
            self.current_photo = None

            if self.history_data:
                self.tree.selection_set("0")
                self.on_select_history()
            else:
                self.set_detail("Chưa có lịch sử cho khu này.")
        except Exception as error:
            messagebox.showerror("Lỗi", str(error), parent=self)

    def on_select_history(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        index = int(selected[0])
        muc = self.history_data[index]
        du_lieu = muc.get("data") or {}
        duong_dan_anh = du_lieu.get("evidence_image", "")

        chi_tiet = [
            f"Thời gian: {muc.get('time', '')}",
            f"Loại: {muc.get('type', '')}",
            f"Nội dung: {muc.get('message', '')}",
            "",
            f"Dữ liệu: {du_lieu}"
        ]
        self.set_detail("\n".join(chi_tiet))

        if duong_dan_anh not in self.history_images:
            self.history_images[duong_dan_anh] = self.tai_anh_url(duong_dan_anh)

        self.current_photo = self.history_images.get(duong_dan_anh)
        if self.current_photo is not None:
            self.image_label.config(image=self.current_photo, text="")
        else:
            self.image_label.config(image="", text="Không có ảnh minh chứng", fg="white")

    def xoa_lich_su(self):
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lịch sử khu này không?", parent=self):
            return
        try:
            response = self.api_delete(f"/api/zones/{self.zone_id}/history", timeout=6)
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không xóa được lịch sử khu."))
            self.tai_lai()
        except Exception as error:
            messagebox.showerror("Lỗi", str(error), parent=self)


class App:
    """Ứng dụng giao diện chính để quản lý và theo dõi các khu."""

    def __init__(self, root):
        self.root = root
        self.root.title("Phần mềm giám sát theo khu")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f0f0")
        self.cards = {}

        top = tk.Frame(root, bg="#1f2937", padx=16, pady=12)
        top.pack(fill="x")

        title = tk.Label(top, text="PHẦN MỀM GIÁM SÁT THEO KHU", fg="white", bg="#1f2937", font=("Arial", 16, "bold"))
        title.pack(side="left")

        button_frame = tk.Frame(top, bg="#1f2937")
        button_frame.pack(side="right")

        tk.Button(button_frame, text="Thêm khu", command=self.on_add_zone).pack(side="left", padx=5)
        tk.Button(button_frame, text="Làm mới", command=self.refresh_view).pack(side="left", padx=5)

        self.status_bar = tk.Label(root, text="Đang khởi động...", anchor="w", bg="#e5e7eb", padx=10, pady=6)
        self.status_bar.pack(fill="x")

        self.canvas = tk.Canvas(root, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_view()

    def set_status(self, text):
        self.status_bar.config(text=text)

    def api_get(self, path, timeout=5):
        return requests.get(SERVER_BASE_URL + path, timeout=timeout)

    def api_post(self, path, json_data, timeout=5):
        return requests.post(SERVER_BASE_URL + path, json=json_data, timeout=timeout)

    def api_delete(self, path, timeout=5):
        return requests.delete(SERVER_BASE_URL + path, timeout=timeout)

    def on_add_zone(self):
        from tkinter import simpledialog
        name = simpledialog.askstring("Thêm khu", "Nhập tên khu mới:", parent=self.root)
        if not name:
            return

        try:
            response = self.api_post("/api/zones", {"name": name.strip()})
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không tạo được khu."))

            self.set_status(f"Đã tạo khu: {data['zone']['name']}")
            self.refresh_view()
        except Exception as error:
            messagebox.showerror("Lỗi", str(error))

    def on_delete_zone(self, zone_id):
        ok = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa khu này không?")
        if not ok:
            return

        try:
            response = self.api_delete(f"/api/zones/{zone_id}")
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không xóa được khu."))

            self.set_status("Đã xóa khu.")
            self.refresh_view()
        except Exception as error:
            messagebox.showerror("Lỗi", str(error))

    def on_zone_settings(self, zone_id):
        try:
            response = self.api_get(f"/api/zones/{zone_id}/settings")
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không tải được cài đặt khu."))

            zone = data["zone"]

            def luu_cai_dat(du_lieu):
                response_save = self.api_post(f"/api/zones/{zone_id}/settings", du_lieu)
                data_save = response_save.json()
                if not response_save.ok or not data_save.get("success"):
                    raise RuntimeError(data_save.get("message", "Không cập nhật được cài đặt khu."))
                self.set_status(f"Đã cập nhật cài đặt cho {zone['name']}")
                self.refresh_view()

            CuaSoCaiDatKhu(self.root, zone, luu_cai_dat)
        except Exception as error:
            messagebox.showerror("Lỗi", str(error))

    def on_zone_history(self, zone_id):
        zone_name = zone_id
        for card_id, card in self.cards.items():
            if card_id == zone_id:
                zone_name = card.title_label.cget("text") or zone_id
                break
        CuaSoLichSuKhu(self.root, zone_id, zone_name, self.api_get, self.api_delete)

    def get_frame_for_zone(self, zone_id):
        try:
            response = self.api_get(f"/api/frame/{zone_id}", timeout=1.2)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            return frame
        except Exception:
            frame = np.zeros((CARD_IMAGE_HEIGHT, CARD_IMAGE_WIDTH, 3), dtype=np.uint8)
            cv2.putText(frame, "Khong lay duoc anh", (20, CARD_IMAGE_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            return frame

    def refresh_view(self):
        try:
            response = self.api_get("/api/zones", timeout=1.5)
            data = response.json()
            if not response.ok or not data.get("success"):
                raise RuntimeError(data.get("message", "Không tải được danh sách khu."))

            zones_data = data.get("zones", [])
        except Exception as error:
            self.set_status(f"Lỗi kết nối server: {error}")
            self.root.after(REFRESH_MS, self.refresh_view)
            return

        active_ids = {zone["id"] for zone in zones_data}

        for zone_id in list(self.cards.keys()):
            if zone_id not in active_ids:
                self.cards[zone_id].destroy()
                del self.cards[zone_id]

        columns = 2

        for index, zone in enumerate(zones_data):
            zone_id = zone["id"]
            if zone_id not in self.cards:
                self.cards[zone_id] = TheKhu(
                    self.scrollable_frame,
                    zone_id,
                    self.on_delete_zone,
                    self.on_zone_settings,
                    self.on_zone_history
                )

            row = index // columns
            column = index % columns
            self.cards[zone_id].grid(row=row, column=column)

            frame = None
            if self.cards[zone_id].can_update_frame(zone):
                frame = self.get_frame_for_zone(zone_id)

            self.cards[zone_id].update(zone, frame)

        if not zones_data:
            self.set_status("Chưa có khu nào.")
        else:
            self.set_status(f"Tổng số khu: {len(zones_data)} | Cập nhật giao diện thành công")

        self.root.after(REFRESH_MS, self.refresh_view)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
