package com.example.appgiamsat;

import android.content.Context;

import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;

import java.util.concurrent.TimeUnit;

public class LapLichThongBaoNen {
    private static final String TEN_TAC_VU = "kiem_tra_canh_bao_lua";

    public static void Bat(Context context) {
        PeriodicWorkRequest yeuCau = new PeriodicWorkRequest.Builder(
                TacVuKiemTraCanhBaoWorker.class,
                15,
                TimeUnit.MINUTES
        ).build();

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                TEN_TAC_VU,
                ExistingPeriodicWorkPolicy.UPDATE,
                yeuCau
        );
    }
}
