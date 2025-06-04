import numpy as np
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────
# 0) パラメータ設定
# ───────────────────────────────────────────────
Va   = 20.0          # HF 電圧振幅 [V]
f_h  = 1000.0        # HF 周波数 [Hz]
omega_h = 2*np.pi*f_h

Ld, Lq = 1e-3, 1.4e-3    # d/q インダクタンス [H]
R_s   = 0.03              # ステータ抵抗 [Ω]

Ts   = 1e-6              # サンプリング周期 [s]
Tend = 0.5              # 解析時間 [s]

# PLL ゲイン
Kp = 100
Ki = 1000                 # Ki ≠ 0 で定常誤差を除去

tau_lpf = 1e-8           # 復調 LPF 時定数 [s]
alpha_lpf = Ts / (tau_lpf + Ts)

# 真値
theta_true = 0.0         # 定常角
omega_true = 0.0         # 速度 0  (≠0 にしても可)

# 推定初期値を -70° に
theta_est = np.deg2rad(-30)
omega_est = 0.0

# ───────────────────────────────────────────────
# 1) ユーティリティ
# ───────────────────────────────────────────────
def wrap(th):
    return (th + np.pi) % (2*np.pi) - np.pi

def rot(alpha, vec):
    c, s = np.cos(alpha), np.sin(alpha)
    return np.array([ c*vec[0] - s*vec[1],
                      s*vec[0] + c*vec[1] ])

# ───────────────────────────────────────────────
# 2) 状態・ログ
# ───────────────────────────────────────────────
Id, Iq = 0.0, 0.0           # dq 電流
# IQ 復調用 LPF 状態 (sin と cos の 2成分ずつ)
ih_s_alpha = ih_s_beta = 0.0
ih_c_alpha = ih_c_beta = 0.0

int_err = 0.0               # PI 積分

t_log, th_log, err_deg_log, i_delta_log, i_gamma_log = [], [], [], [], []

# ───────────────────────────────────────────────
# 3) ループ
# ───────────────────────────────────────────────
steps = int(Tend / Ts)
for k in range(steps):
    t = k * Ts

    # === (1) HF 電圧生成 ===
    Vgamma = Va * np.sin(omega_h * t)
    Vdelta = 0.0
    V_alpha, V_beta = rot(theta_est, np.array([Vgamma, Vdelta]))

    # === (2) dq 電流モデル (Euler, Rs & クロスターム有り) ===
    V_d, V_q = rot(-theta_true, np.array([V_alpha, V_beta]))
    dId = (1/Ld)*(V_d)
    dIq = (1/Lq)*(V_q)
    # dId = (1/Ld)*(V_d - R_s*Id + omega_true*Lq*Iq)
    # dIq = (1/Lq)*(V_q - R_s*Iq - omega_true*Ld*Id)    
    Id += dId * Ts
    Iq += dIq * Ts
    I_alpha, I_beta = rot(theta_true, np.array([Id, Iq]))

    # === (3) I/Q 復調 ===
    sin_ref = np.sin(omega_h * t)
    cos_ref = np.cos(omega_h * t)

    # In‑phase (sin) branchA
    ih_s_alpha += alpha_lpf * (I_alpha * sin_ref - ih_s_alpha)
    ih_s_beta  += alpha_lpf * (I_beta  * sin_ref - ih_s_beta)
    # Quadrature (cos) branch
    ih_c_alpha += alpha_lpf * (I_alpha * cos_ref - ih_c_alpha)
    ih_c_beta  += alpha_lpf * (I_beta  * cos_ref - ih_c_beta)

    # sin², cos² の平均 0.5 を補正 → ×2
    Ih_alpha = 2 * ih_s_alpha   # ここでは sin 分のみ使用
    Ih_beta  = 2 * ih_s_beta

    # αβ → γδ
    Ih_gamma, Ih_delta = rot(-theta_est, np.array([Ih_alpha, Ih_beta]))

    # === (4) PLL (PI) ===
    err = Ih_delta
    int_err += err * Ts
    omega_est = Kp * err + Ki * int_err

    # === (5) 位相推定 ===
    theta_est += omega_est * Ts
    theta_est = wrap(theta_est)

    # === ログ ===
    i_delta_log.append(Ih_delta)
    i_gamma_log.append(Ih_gamma)
    t_log.append(t)
    th_log.append(theta_est)
    err_deg_log.append(np.rad2deg(theta_est - theta_true))

# ───────────────────────────────────────────────
# 4) 描画
# ───────────────────────────────────────────────
plt.figure(figsize=(9,4))
plt.plot(t_log, th_log, label=r'$\hat\theta_{est}$')
plt.axhline(theta_true, color='k', linestyle='--', label=r'$\theta_{true}$')
plt.ylabel('Electrical angle [rad]')
plt.xlabel('Time [s]')
plt.title('Phase tracking with IQ demod + Rs & cross terms')
plt.grid(); plt.legend()

plt.figure(figsize=(9,4))
plt.plot(t_log, err_deg_log)
plt.ylabel('Phase error [deg]')
plt.xlabel('Time [s]')
plt.title('Phase error convergence')
plt.grid()

# plt.figure(figsize=(9,4))
# plt.plot(t_log, i_delta_log)
# plt.ylabel('i_delta [A]')
# plt.xlabel('Time [s]')
# plt.title('delta current')
# plt.grid()

plt.figure(figsize=(9,4))
plt.plot(t_log, i_gamma_log)
plt.ylabel('i_gamma [A]')
plt.xlabel('Time [s]')
plt.title('gamma current')
plt.grid()

plt.tight_layout()
plt.show()
