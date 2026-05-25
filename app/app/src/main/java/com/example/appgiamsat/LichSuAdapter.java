package com.example.appgiamsat;

import android.graphics.Bitmap;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// Adapter hiển thị danh sách lịch sử sự cố trong màn hình chi tiết khu.
public class LichSuAdapter extends RecyclerView.Adapter<LichSuAdapter.LichSuViewHolder> {

    private final List<LichSuSuCo> danhSach;
    private final ExecutorService luongTaiAnh = Executors.newFixedThreadPool(2);

    public LichSuAdapter(List<LichSuSuCo> danhSach) {
        this.danhSach = danhSach;
    }

    @NonNull
    @Override
    public LichSuViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_lich_su, parent, false);
        return new LichSuViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull LichSuViewHolder holder, int position) {
        LichSuSuCo muc = danhSach.get(position);
        holder.txtNoiDung.setText(muc.getNoiDung());
        holder.txtThoiGian.setText(muc.getThoiGian());
        holder.imgMinhChung.setVisibility(View.GONE);
        holder.imgMinhChung.setImageDrawable(null);

        String urlAnh = CauHinhServer.ChuanHoaUrlAnhMinhChung(muc.getDuongDanAnhMinhChung());
        if (urlAnh == null || urlAnh.trim().isEmpty()) {
            return;
        }

        luongTaiAnh.execute(() -> {
            Bitmap bitmap = TaiDuLieuMang.TaiAnhBitmap(urlAnh);
            holder.imgMinhChung.post(() -> {
                if (bitmap != null) {
                    holder.imgMinhChung.setImageBitmap(bitmap);
                    holder.imgMinhChung.setVisibility(View.VISIBLE);
                } else {
                    holder.imgMinhChung.setVisibility(View.GONE);
                }
            });
        });
    }

    @Override
    public int getItemCount() {
        return danhSach.size();
    }

    static class LichSuViewHolder extends RecyclerView.ViewHolder {
        TextView txtNoiDung;
        TextView txtThoiGian;
        ImageView imgMinhChung;

        public LichSuViewHolder(@NonNull View itemView) {
            super(itemView);
            txtNoiDung = itemView.findViewById(R.id.txtNoiDungLichSu);
            txtThoiGian = itemView.findViewById(R.id.txtThoiGianLichSu);
            imgMinhChung = itemView.findViewById(R.id.imgMinhChungLichSu);
        }
    }
}
