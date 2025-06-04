import numpy as np
import matplotlib.pyplot as plt

# ── 0) モータ & フィルタ共通パラメータ ────────────────────
Va, f_h = 25.0, 1_000.0
ωh = 2*np.pi*f_h
Ld, Lq = 1e-3, 1.4e-3
R_s = 0.03
Ts, Tend = 1/6000*2, 0.05

rpm, Pn = 2000, 4
ω_true = rpm/60 * 2*np.pi * Pn          # 真の電気角速度

# ── 1) ユーティリティ ───────────────────────────────
def wrap(th): return (th + np.pi) % (2*np.pi) - np.pi
def rot(a,v):
    c,s = np.cos(a), np.sin(a)
    return np.array([ c*v[0]-s*v[1],  s*v[0]+c*v[1] ])

def f_discrete(x,u):                    # 状態遷移
    Id,Iq,th,ω = x;  Vα,Vβ = u
    Vd,Vq = rot(-th, [Vα,Vβ])
    Id += Ts/Ld*(Vd - R_s*Id + ω*Lq*Iq)
    Iq += Ts/Lq*(Vq - R_s*Iq - ω*Ld*Id)
    th  = wrap(th + ω*Ts)
    return np.array([Id,Iq,th,ω])       # ω̇=0

def h_meas(x):                          # 観測
    Id,Iq,th,_ = x
    return rot(th, [Id,Iq])             # Iαβ

# ── 2) UKF シグマ点生成 & 変換 ──────────────────────
n = 4                                   # 次元
alpha, beta, kappa = 1e-3, 2.0, 0.0
lam = alpha**2 * (n+kappa) - n
gamma = np.sqrt(n + lam)

Wm = np.full(2*n+1, 0.5/(n+lam))
Wc = Wm.copy()
Wm[0] = lam/(n+lam);  Wc[0] = Wm[0] + (1-alpha**2+beta)

def sigma_points(x,P):
    S = np.linalg.cholesky(P + 1e-12*np.eye(n))
    sig = np.empty((2*n+1, n)); sig[0] = x
    for i in range(n):
        d = gamma * S[:,i]
        sig[ i+1]   = x + d
        sig[n+i+1] = x - d
    sig[:,2] = np.vectorize(wrap)(sig[:,2])  # θ 行正規化
    return sig

def unscented_transform(sig, noise_cov, mean_fun=None, angle_idx=None):
    if mean_fun is None:
        mean = np.sum(Wm[:, None]*sig, axis=0)
    else:
        mean = mean_fun(sig)

    diff = sig - mean
    if angle_idx is not None:
        diff[:, angle_idx] = np.vectorize(wrap)(diff[:, angle_idx])

    cov = diff.T @ (Wc[:, None]*diff) + noise_cov
    return mean, cov, diff

# ── 3) ノイズ & 初期化 ───────────────────────────────
Q = np.diag([1e-6,1e-6,1e-6,10.0])
R = np.diag([1e-4,1e-4])

x_true = np.array([0,0,0,ω_true])
x_est  = np.array([0,0,np.deg2rad(30),0])
P      = np.diag([1e-3,1e-3,(np.pi/2)**2, 100**2])

rng = np.random.default_rng(0)

# ── 4) ループ ──────────────────────────────────────
t_log, th_true_log, th_est_log, err_log = [],[],[],[]
steps = int(Tend/Ts)

for k in range(steps):
    t = k*Ts

    # HF 電圧 (推定角で回転)
    Vγ = Va*np.sin(ωh*t);  Vδ = 0.0
    Vαβ = rot(x_est[2], [Vγ,Vδ])

    # ----- 真値更新 -----
    x_true = f_discrete(x_true, Vαβ)
    y = h_meas(x_true) + rng.normal(0,np.sqrt(R[0,0]),2)

    # ----- UKF 予測 -----
    sig = sigma_points(x_est, P)
    sig_f = np.array([f_discrete(s,Vαβ) for s in sig])
    # x_pred, P_pred, diff_f = unscented_transform(sig_f, Q)
    x_pred, P_pred, diff_f = unscented_transform(sig_f, Q, angle_idx=2)

    # ----- UKF 更新 -----
    sig_h = np.array([h_meas(s) for s in sig_f])
    # y_pred, Pyy, diff_h = unscented_transform(sig_h, R,
                  #  mean_fun=lambda s: np.sum(Wm[:,None]*s,axis=0))
    y_pred, Pyy, diff_h = unscented_transform(
        sig_h, R, mean_fun=lambda s: np.sum(Wm[:,None]*s,axis=0),
        angle_idx=None)

    Pxy = diff_f.T @ (Wc[:,None]*diff_h)
    K   = Pxy @ np.linalg.inv(Pyy)

    x_est = x_pred + K @ (y - y_pred)
    x_est[2] = wrap(x_est[2])
    P = P_pred - K @ Pyy @ K.T

    # ----- ログ -----
    t_log.append(t)
    th_true_log.append(np.rad2deg(x_true[2]))
    th_est_log .append(np.rad2deg(x_est [2]))
    err_log    .append(np.rad2deg(wrap(x_est[2]-x_true[2])))

# ── 5) 可視化 ──────────────────────────────────────
plt.figure(figsize=(10,4))
plt.plot(t_log, th_true_log, label='θ true')
plt.plot(t_log, th_est_log , '--', label='θ UKF')
plt.ylabel('Electrical angle [deg]'); plt.xlabel('Time [s]')
plt.title('UKF phase tracking'); plt.grid(); plt.legend()

plt.figure(figsize=(10,3))
plt.plot(t_log, err_log)
plt.ylabel('Error [deg]'); plt.xlabel('Time [s]')
plt.title('Phase estimation error (UKF)'); plt.grid()
plt.tight_layout(); plt.show()
