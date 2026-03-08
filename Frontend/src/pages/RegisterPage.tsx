import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email || !password || !confirm) { setError('Please fill in all fields'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    if (password !== confirm) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      await register({ email, password });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
          --bg: #f7f7f5;
          --card: #ffffff;
          --border: #e8e8e4;
          --ink: #111110;
          --muted: #888882;
          --error: #d93025;
          --input-bg: #fafaf8;
        }

        body {
          background: var(--bg);
          font-family: 'DM Sans', sans-serif;
          color: var(--ink);
          min-height: 100vh;
        }

        .page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          background: var(--bg);
          background-image: radial-gradient(circle, #d4d4cc 1px, transparent 1px);
          background-size: 28px 28px;
        }

        .card {
          background: var(--card);
          border: 1px solid var(--border);
          border-radius: 20px;
          padding: 48px 44px;
          width: 100%;
          max-width: 420px;
          box-shadow:
            0 1px 2px rgba(0,0,0,0.04),
            0 8px 32px rgba(0,0,0,0.06),
            0 24px 64px rgba(0,0,0,0.04);
          animation: rise 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
        }

        @keyframes rise {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 36px;
        }

        .logo-mark {
          width: 32px; height: 32px;
          background: var(--ink);
          border-radius: 8px;
          display: flex; align-items: center; justify-content: center;
          font-size: 16px;
        }

        .logo-name {
          font-family: 'Bricolage Grotesque', sans-serif;
          font-size: 17px;
          font-weight: 700;
          color: var(--ink);
          letter-spacing: -0.02em;
        }

        .card-title {
          font-family: 'Bricolage Grotesque', sans-serif;
          font-size: 26px;
          font-weight: 700;
          color: var(--ink);
          letter-spacing: -0.03em;
          margin-bottom: 6px;
        }

        .card-sub {
          font-size: 14px;
          color: var(--muted);
          margin-bottom: 32px;
        }

        .field { margin-bottom: 14px; }

        .field label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          color: var(--ink);
          margin-bottom: 7px;
        }

        .field input {
          width: 100%;
          padding: 12px 14px;
          background: var(--input-bg);
          border: 1.5px solid var(--border);
          border-radius: 10px;
          color: var(--ink);
          font-family: 'DM Sans', sans-serif;
          font-size: 15px;
          outline: none;
          transition: border-color 0.15s, box-shadow 0.15s;
        }

        .field input::placeholder { color: #bbbbb5; }

        .field input:focus {
          border-color: var(--ink);
          box-shadow: 0 0 0 3px rgba(17,17,16,0.08);
          background: #fff;
        }

        .field input.err {
          border-color: var(--error);
          box-shadow: 0 0 0 3px rgba(217,48,37,0.08);
        }

        .error-box {
          display: flex;
          align-items: center;
          gap: 8px;
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: 9px;
          padding: 10px 13px;
          font-size: 13px;
          color: var(--error);
          margin-bottom: 16px;
          animation: shake 0.3s ease;
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }

        .submit {
          width: 100%;
          padding: 13px;
          margin-top: 8px;
          background: var(--ink);
          border: none;
          border-radius: 10px;
          color: #ffffff;
          font-family: 'DM Sans', sans-serif;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s;
          letter-spacing: -0.01em;
        }

        .submit:hover:not(:disabled) {
          background: #2a2a28;
          transform: translateY(-1px);
          box-shadow: 0 4px 16px rgba(17,17,16,0.2);
        }

        .submit:active:not(:disabled) { transform: translateY(0); }
        .submit:disabled { opacity: 0.5; cursor: not-allowed; }

        .footer-link {
          margin-top: 20px;
          text-align: center;
          font-size: 14px;
          color: var(--muted);
        }

        .footer-link a {
          color: var(--ink);
          text-decoration: none;
          font-weight: 500;
          border-bottom: 1px solid var(--border);
          padding-bottom: 1px;
          transition: border-color 0.15s;
        }

        .footer-link a:hover { border-color: var(--ink); }

        .spinner {
          display: inline-block;
          width: 15px; height: 15px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
          margin-right: 8px;
          vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>

      <div className="page">
        <div className="card">

          <div className="logo">
            <div className="logo-mark">🏨</div>
            <span className="logo-name">HotelApp</span>
          </div>

          <h1 className="card-title">Create account</h1>
          <p className="card-sub">Sign up to get started</p>

          {error && (
            <div className="error-box">
              <span>⚠</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={error ? 'err' : ''}
                autoFocus
                autoComplete="email"
              />
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Min. 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={error ? 'err' : ''}
                autoComplete="new-password"
              />
            </div>

            <div className="field">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Repeat your password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className={error ? 'err' : ''}
                autoComplete="new-password"
              />
            </div>

            <button type="submit" className="submit" disabled={loading}>
              {loading && <span className="spinner" />}
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <div className="footer-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>

        </div>
      </div>
    </>
  );
}