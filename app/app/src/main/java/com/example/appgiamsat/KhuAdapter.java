package com.example.appgiamsat;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.card.MaterialCardView;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

// Adapter dùng để hiển thị danh sách các khu lên RecyclerView.
public class KhuAdapter extends RecyclerView.Adapter<KhuAdapter.KhuViewHolder> {

    private final Context context;
    private final List<Khu> danhSachKhu;
    private final ExecutorService luongNen = Executors.newFixedThreadPool(3);
    private final ConcurrentHashMap<String, AtomicInteger> boDemPhienTaiAnh = new ConcurrentHashMap<>();

    public KhuAdapter(Context context, List<Khu> danhSachKhu) {
        this.context = context;
        this.danhSachKhu = danhSachKhu;
    }

    @NonNull
    @Override
    public KhuViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_khu, parent, false);
        return new KhuViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull KhuViewHolder holder, int position) {
        Khu khu = danhSachKhu.get(position);

        holder.txtTenKhu.setText(khu.getTenKhu());
        holder.txtTrangThai.setText(khu.getTrangThai());
        holder.txtThoiGian.setText(khu.getThoiGianCapNhat());

        // Chỉ gán placeholder khi ô ảnh hiện chưa có ảnh, tránh nhấp nháy mỗi lần refresh.
        if (!(holder.imgKhu.getDrawable() instanceof BitmapDrawable)) {
            holder.imgKhu.setImageResource(R.drawable.bg_khu_placeholder);
        }

        // Mỗi lần tải ảnh sẽ tăng mã phiên, ảnh cũ về muộn sẽ bị bỏ.
        AtomicInteger boDem = boDemPhienTaiAnh.computeIfAbsent(khu.getMaKhu(), key -> new AtomicInteger(0));
        int phienHienTai = boDem.incrementAndGet();

        luongNen.execute(() -> {
            Bitmap bitmap = TaiDuLieuMang.TaiAnhBitmap(khu.getUrlAnh());
            holder.imgKhu.post(() -> {
                AtomicInteger boDemKiemTra = boDemPhienTaiAnh.get(khu.getMaKhu());
                if (boDemKiemTra == null || phienHienTai != boDemKiemTra.get()) {
                    return;
                }

                if (bitmap != null) {
                    holder.imgKhu.setImageBitmap(bitmap);
                } else if (!(holder.imgKhu.getDrawable() instanceof BitmapDrawable)) {
                    if (khu.isCanhBao()) {
                        holder.imgKhu.setImageResource(R.drawable.bg_khu_2);
                    } else if (khu.isCoDuLieu()) {
                        holder.imgKhu.setImageResource(R.drawable.bg_khu_1);
                    } else {
                        holder.imgKhu.setImageResource(R.drawable.bg_khu_placeholder);
                    }
                }
            });
        });

        if (khu.isCanhBao()) {
            holder.layoutTrangThai.setBackgroundResource(R.drawable.bg_badge_canh_bao);
            holder.txtTrangThai.setTextColor(context.getColor(R.color.trangThaiLoi));
            holder.cardKhu.setCardBackgroundColor(context.getColor(R.color.mauTheNoiBat));
            holder.cardKhu.setStrokeColor(context.getColor(R.color.trangThaiLoi));
            holder.cardKhu.setStrokeWidth(2);

        } else if (!khu.isCoDuLieu()) {
            holder.layoutTrangThai.setBackgroundResource(R.drawable.bg_badge_cho);
            holder.txtTrangThai.setTextColor(context.getColor(R.color.trangThaiCho));
            holder.cardKhu.setCardBackgroundColor(context.getColor(R.color.mauNenThe));
            holder.cardKhu.setStrokeWidth(0);
        } else {
            holder.layoutTrangThai.setBackgroundResource(R.drawable.bg_badge_hoat_dong);
            holder.txtTrangThai.setTextColor(context.getColor(R.color.trangThaiTot));
            holder.cardKhu.setCardBackgroundColor(context.getColor(R.color.white));
            holder.cardKhu.setStrokeWidth(0);
        }

        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(context, ChiTietKhuActivity.class);
            intent.putExtra("maKhu", khu.getMaKhu());
            intent.putExtra("tenKhu", khu.getTenKhu());
            intent.putExtra("trangThai", khu.getTrangThai());
            intent.putExtra("thoiGian", khu.getThoiGianCapNhat());
            intent.putExtra("soPhatHien", khu.getSoPhatHien());
            intent.putExtra("moTa", khu.getMoTa());
            intent.putExtra("canhBao", khu.isCanhBao());
            intent.putExtra("coDuLieu", khu.isCoDuLieu());
            intent.putExtra("urlAnh", khu.getUrlAnh());
            context.startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return danhSachKhu.size();
    }

    static class KhuViewHolder extends RecyclerView.ViewHolder {
        MaterialCardView cardKhu;
        ImageView imgKhu;
        TextView txtTenKhu;
        TextView txtTrangThai;
        TextView txtThoiGian;
        LinearLayout layoutTrangThai;

        public KhuViewHolder(@NonNull View itemView) {
            super(itemView);
            cardKhu = itemView.findViewById(R.id.cardKhu);
            imgKhu = itemView.findViewById(R.id.imgKhu);
            txtTenKhu = itemView.findViewById(R.id.txtTenKhu);
            txtTrangThai = itemView.findViewById(R.id.txtTrangThai);
            txtThoiGian = itemView.findViewById(R.id.txtThoiGian);
            layoutTrangThai = itemView.findViewById(R.id.layoutTrangThai);
        }
    }
}
