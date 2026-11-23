"""
The first-cell-height calculation we did by hand on 29 June 2026 (calculations/hand-calculation.jpg),
step by step, with the same inputs. Run:  python -m deaerator.calc

Inputs (water at about 20 °C, the outer radius of the sector, 1000 rpm):
  rho = 998.2 kg/m^3, mu = 1.003e-3 Pa s, r = L = 0.05 m, N = 1000 rpm
Steps:
  omega = 2 pi N / 60                         angular speed
  V     = omega r                             tip speed, the velocity scale
  Re    = rho V L / mu
  Cf    = 0.026 / Re^(1/7)                    turbulent flat-plate skin friction
  q     = rho V^2 / 2,  tau_w = Cf q          dynamic pressure, wall shear stress
  u_tau = sqrt(tau_w / rho)                   friction velocity
  y     = y+ mu / (rho u_tau)                 first-cell height for a target y+
"""
import math

RHO = 998.2          # kg/m^3, water
MU = 1.003e-3        # Pa s, water
R_OUTER = 0.05       # m
RPM = 1000.0


def chain(rho=RHO, mu=MU, r=R_OUTER, rpm=RPM, L=None):
    L = r if L is None else L
    omega = 2 * math.pi * rpm / 60
    V = omega * r
    Re = rho * V * L / mu
    Cf = 0.026 / Re ** (1 / 7)
    q = 0.5 * rho * V ** 2
    tau = Cf * q
    u_tau = math.sqrt(tau / rho)
    return {'omega': omega, 'V': V, 'Re': Re, 'Cf': Cf, 'q': q, 'tau_w': tau, 'u_tau': u_tau}


def first_cell(y_plus, c=None, rho=RHO, mu=MU):
    c = c or chain()
    return y_plus * mu / (rho * c['u_tau'])


def y_plus_of(y, c=None, rho=RHO, mu=MU):
    c = c or chain()
    return rho * c['u_tau'] * y / mu


def laminar_bl_thickness(c=None, L=R_OUTER):
    """Blasius 99% thickness, 5 L / sqrt(Re): the yardstick for a laminar run."""
    c = c or chain()
    return 5.0 * L / math.sqrt(c['Re'])


if __name__ == '__main__':
    c = chain()
    print(f"omega  = {c['omega']:.2f} rad/s          (hand: 104.72)")
    print(f"V      = {c['V']:.3f} m/s            (hand: 5.236)")
    print(f"Re     = {c['Re']:.4g}             (hand: 2.61e5)")
    print(f"Cf     = {c['Cf']:.5f}             (hand: 0.00438)")
    print(f"q      = {c['q']:.0f} Pa             (hand: 13684)")
    print(f"tau_w  = {c['tau_w']:.1f} Pa              (hand: 60)")
    print(f"u_tau  = {c['u_tau']:.3f} m/s            (hand: 0.245)")
    for yp, hand in ((1, '4.1e-6'), (5, '2e-5'), (30, '1.23e-4')):
        print(f"y(y+={yp:2d}) = {first_cell(yp, c):.3g} m        (hand: {hand})")
    print(f"y+ of the uniform mesh's first cell, 1/9 mm: {y_plus_of(1e-3 / 9, c):.1f}")
    print(f"y+ of 0.0048 mm (slides): {y_plus_of(0.0048e-3, c):.2f};  of 0.02 mm: {y_plus_of(0.02e-3, c):.2f}")
    print(f"laminar boundary layer, 5L/sqrt(Re): {laminar_bl_thickness(c) * 1e3:.2f} mm")
    print(f"centrifugal acceleration at r = 10, 50 mm: {c['omega']**2 * 0.01:.0f}, {c['omega']**2 * 0.05:.0f} m/s^2 "
          f"({c['omega']**2 * 0.01 / 9.81:.0f} g, {c['omega']**2 * 0.05 / 9.81:.0f} g)")
