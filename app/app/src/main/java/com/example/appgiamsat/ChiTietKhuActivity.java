package com.example.appgiamsat;

import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class ChiTietKhuActivity extends AppCompatActivity {

    private static final long CHU_KY_LAM_MOI_ANH_MS = 1500;
    private static final long CHU_KY_LAM_MOI_LICH_SU_MS = 5000;

    private ImageView imgChiTiet;
    private String urlAnh;
    private String maKhu;
    private boolean canhBao;
    private boolean coDuLieu;
    private RecyclerView recyclerLichSu;
    private final List<LichSuSuCo> danhSachLichSu = new ArrayList<>();
    private LichSuAdapter lichSuAdapter;
    private final ExecutorService luongTaiAnh = Executors.newSingleThreadExecutor();
    private final ExecutorService luongTaiLichSu = Executors.newSingleThreadExecutor();
    private final AtomicInteger boDemPhienAnh = new AtomicInteger(0);

    private final Handler handlerLamMoiAnh = new Handler(Looper.getMainLooper());
    private final Handler handlerLamMoiLichSu = new Handler(Looper.getMainLooper());

    private final Runnable tacVuLamMoiAnh = new Runnable() {
        @Override
        public void run() {
            TaiLaiAnhChiTiet();
            handlerLamMoiAnh.postDelayed(this, CHU_KY_LAM_MOI_ANH_MS);
        }
    };

    private final Runnable tacVuLamMoiLichSu = new Runnable() {
        @Override
        public void run() {
            TaiLichSuKhu();
            handlerLamMoiLichSu.postDelayed(this, CHU_KY_LAM_MOI_LICH_SU_MS);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chi_tiet_khu);

        ImageButton btnQuayLai = findViewById(R.id.btnQuayLai);
        ImageButton btnThem = findViewById(R.id.btnThemTuyChon);
        TextView txtTieuDe = findViewById(R.id.txtTieuDeKhu);
        imgChiTiet = findViewById(R.id.imgChiTietKhu);
        recyclerLichSu = findViewById(R.id.recyclerLichSu);
        TextView txtTrangThaiLichSu = findViewById(R.id.txtTrangThaiLichSu);

        maKhu = getIntent().getStringExtra("maKhu");
        String tenKhu = getIntent().getStringExtra("tenKhu");
        urlAnh = getIntent().getStringExtra("urlAnh");
        canhBao = getIntent().getBooleanExtra("canhBao", false);
        coDuLieu = getIntent().getBooleanExtra("coDuLieu", true);

        txtTieuDe.setText(tenKhu);
        imgChiTiet.setImageResource(R.drawable.bg_khu_placeholder);

        recyclerLichSu.setLayoutManager(new LinearLayoutManager(this));
        recyclerLichSu.setNestedScrollingEnabled(true);
        lichSuAdapter = new LichSuAdapter(danhSachLichSu);
        recyclerLichSu.setAdapter(lichSuAdapter);
        txtTrangThaiLichSu.setText("Đang tải lịch sử...");

        TaiLaiAnhChiTiet();
        TaiLichSuKhu();

        btnQuayLai.setOnClickListener(v -> finish());
        btnThem.setOnClickListener(v -> {
            // Giữ nút này để giống mockup. Có thể gắn menu sau.
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        handlerLamMoiAnh.postDelayed(tacVuLamMoiAnh, CHU_KY_LAM_MOI_ANH_MS);
        handlerLamMoiLichSu.postDelayed(tacVuLamMoiLichSu, CHU_KY_LAM_MOI_LICH_SU_MS);
    }

    @Override
    protected void onPause() {
        super.onPause();
        handlerLamMoiAnh.removeCallbacks(tacVuLamMoiAnh);
        handlerLamMoiLichSu.removeCallbacks(tacVuLamMoiLichSu);
    }

    private void TaiLaiAnhChiTiet() {
        int phienHienTai = boDemPhienAnh.incrementAndGet();
        luongTaiAnh.execute(() -> {
            Bitmap bitmap = TaiDuLieuMang.TaiAnhBitmap(urlAnh);
            imgChiTiet.post(() -> {
                if (phienHienTai != boDemPhienAnh.get()) {
                    return;
                }

                if (bitmap != null) {
                    imgChiTiet.setImageBitmap(bitmap);
                } else if (canhBao) {
                    imgChiTiet.setImageResource(R.drawable.bg_khu_2);
                } else if (coDuLieu) {
                    imgChiTiet.setImageResource(R.drawable.bg_khu_1);
                } else {
                    imgChiTiet.setImageResource(R.drawable.bg_khu_placeholder);
                }
            });
        });
    }

    private void TaiLichSuKhu() {
        luongTaiLichSu.execute(() -> {
            try {
                List<LichSuSuCo> lichSu = TaiDuLieuMang.LayLichSuKhu(maKhu);
                recyclerLichSu.post(() -> {
                    danhSachLichSu.clear();
                    danhSachLichSu.addAll(lichSu);
                    lichSuAdapter.notifyDataSetChanged();

                    TextView txtTrangThaiLichSu = findViewById(R.id.txtTrangThaiLichSu);
                    if (lichSu.isEmpty()) {
                        txtTrangThaiLichSu.setText("Chưa có lịch sử.");
                    } else {
                        txtTrangThaiLichSu.setText("Cuộn xuống để xem các ảnh minh chứng.");
                    }
                });
            } catch (Exception e) {
                recyclerLichSu.post(() -> {
                    TextView txtTrangThaiLichSu = findViewById(R.id.txtTrangThaiLichSu);
                    txtTrangThaiLichSu.setText("Không tải được lịch sử từ server.");

                    if (danhSachLichSu.isEmpty()) {
                        danhSachLichSu.clear();
                        danhSachLichSu.add(new LichSuSuCo("--", "Chưa có dữ liệu lịch sử hoặc server chưa ghi log."));
                        lichSuAdapter.notifyDataSetChanged();
                    }
                });
            }
        });
    }
}
