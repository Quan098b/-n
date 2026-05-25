package com.example.appgiamsat;

import android.Manifest;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

// Màn hình chính hiển thị danh sách các khu giám sát và tự làm mới dữ liệu theo chu kỳ.
public class MainActivity extends AppCompatActivity {

    private static final long CHU_KY_LAM_MOI_MS = 4000;

    private final ActivityResultLauncher<String> xinQuyenThongBao = registerForActivityResult(
            new ActivityResultContracts.RequestPermission(),
            ketQua -> FirebaseTokenHelper.LayVaDangKyLaiToken(this, false)
    );

    private RecyclerView recyclerKhu;
    private KhuAdapter khuAdapter;
    private final List<Khu> danhSachKhu = new ArrayList<>();
    private TextView txtTrangThaiKetNoi;
    private View chamTrangThai;

    private final Handler handlerLamMoi = new Handler(Looper.getMainLooper());

    private final Runnable tacVuLamMoi = new Runnable() {
        @Override
        public void run() {
            TaiDanhSachKhuThat(false);
            handlerLamMoi.postDelayed(this, CHU_KY_LAM_MOI_MS);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        recyclerKhu = findViewById(R.id.recyclerKhu);
        ImageButton btnLamMoi = findViewById(R.id.btnLamMoi);
        txtTrangThaiKetNoi = findViewById(R.id.txtTrangThaiKetNoi);
        chamTrangThai = findViewById(R.id.chamTrangThaiServer);

        recyclerKhu.setLayoutManager(new LinearLayoutManager(this));
        khuAdapter = new KhuAdapter(this, danhSachKhu);
        recyclerKhu.setAdapter(khuAdapter);

        BoXuLyThongBao.TaoKenhThongBao(this);
        XinQuyenThongBaoNeuCan();
        FirebaseTokenHelper.LayVaDangKyLaiToken(this, false);

        TaiDanhSachKhuThat(true);
        btnLamMoi.setOnClickListener(v -> TaiDanhSachKhuThat(true));
    }

    @Override
    protected void onResume() {
        super.onResume();
        handlerLamMoi.postDelayed(tacVuLamMoi, CHU_KY_LAM_MOI_MS);
        FirebaseTokenHelper.LayVaDangKyLaiToken(this, true);
    }

    @Override
    protected void onPause() {
        super.onPause();
        handlerLamMoi.removeCallbacks(tacVuLamMoi);
    }

    private void XinQuyenThongBaoNeuCan() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                xinQuyenThongBao.launch(Manifest.permission.POST_NOTIFICATIONS);
            }
        }
    }

    private void TaiDanhSachKhuThat(boolean hienTrangThaiDangTai) {
        if (hienTrangThaiDangTai) {
            txtTrangThaiKetNoi.setText("Đang tải dữ liệu...");
            chamTrangThai.setBackgroundResource(R.drawable.bg_cham_vang);
        }

        ExecutorService luongNen = Executors.newSingleThreadExecutor();
        luongNen.execute(() -> {
            try {
                List<Khu> duLieuThat = TaiDuLieuMang.LayDanhSachKhuTuServer();

                runOnUiThread(() -> {
                    boolean coThayDoi = !danhSachKhu.equals(duLieuThat);

                    if (coThayDoi) {
                        danhSachKhu.clear();
                        danhSachKhu.addAll(duLieuThat);
                        khuAdapter.notifyDataSetChanged();
                    }

                    txtTrangThaiKetNoi.setText("Đã kết nối");
                    chamTrangThai.setBackgroundResource(R.drawable.bg_cham_xanh);
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    txtTrangThaiKetNoi.setText("Mất kết nối");
                    chamTrangThai.setBackgroundResource(R.drawable.bg_cham_do);

                    if (danhSachKhu.isEmpty()) {
                        danhSachKhu.clear();
                        danhSachKhu.addAll(TaoDuLieuMau());
                        khuAdapter.notifyDataSetChanged();
                    }
                });
            }
        });
    }

    private List<Khu> TaoDuLieuMau() {
        List<Khu> ds = new ArrayList<>();

        ds.add(new Khu("khu_1", "Khu 1", "Đang hoạt động", "10:30", 0,
                "Vị trí: Kho hàng trung tâm - Tầng 1", false, true, CauHinhServer.LayUrlAnhKhu("khu_1")));

        ds.add(new Khu("khu_2", "Khu 2", "Đang hoạt động", "10:31", 2,
                "Vị trí: Gian bếp trung tâm - Tầng 1", true, true, CauHinhServer.LayUrlAnhKhu("khu_2")));

        ds.add(new Khu("khu_3", "Khu 3", "Chưa có dữ liệu", "10:29", 0,
                "Vị trí: Hành lang phía sau - Tầng 2", false, false, CauHinhServer.LayUrlAnhKhu("khu_3")));

        return ds;
    }
}
