import { useEffect, useState } from "react";
import {
  Check,
  LockKeyhole,
  Monitor,
  ShieldCheck,
  UserRound,
} from "lucide-react";
import { api } from "./api";
type Account = {
  username: string;
  display_name: string;
  email: string;
  joined_at: string;
};
type Device = {
  id: number;
  device: string;
  created_at: string;
  current: boolean;
};
export default function AccountSettings({
  onUpdated,
}: {
  onUpdated: () => void;
}) {
  const [account, setAccount] = useState<Account | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [name, setName] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    Promise.allSettled([
      api<Account>("account/"),
      api<Device[]>("account/sessions/"),
    ]).then(([profile, sessions]) => {
      if (!alive) return;
      if (profile.status === "fulfilled") {
        setAccount(profile.value);
        setName(profile.value.display_name);
      } else setStatus(String(profile.reason));
      if (sessions.status === "fulfilled") setDevices(sessions.value);
    });
    return () => {
      alive = false;
    };
  }, []);
  return (
    <section className="account-page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">YOUR SPACE, YOUR SETTINGS</span>
          <h1>Account & security</h1>
          <p>Manage how you appear and where you’re signed in.</p>
        </div>
        <ShieldCheck size={38} />
      </div>
      <div className="account-grid">
        <section className="surface-card">
          <div className="card-heading">
            <UserRound size={21} />
            <h2>Your profile</h2>
          </div>
          {account ? (
            <form
              onSubmit={async (event) => {
                event.preventDefault();
                setBusy(true);
                try {
                  setAccount(
                    await api<Account>("account/", {
                      method: "PUT",
                      body: JSON.stringify({ display_name: name }),
                    }),
                  );
                  setStatus("Your profile has been updated.");
                  onUpdated();
                } catch (error) {
                  setStatus((error as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              <label htmlFor="profile-name">
                Display name
                <input
                  id="profile-name"
                  value={name}
                  maxLength={100}
                  disabled={busy}
                  onChange={(event) => setName(event.target.value)}
                />
              </label>
              <label>
                Username
                <input value={account.username} readOnly />
              </label>
              <label>
                Email address
                <input value={account.email} readOnly />
              </label>
              <small>
                Username and email remain your account identifiers. A verified
                email-change workflow is not enabled.
              </small>
              <button className="button" disabled={busy}>
                <Check size={16} />
                Save profile
              </button>
            </form>
          ) : (
            <p>Loading your profile…</p>
          )}
        </section>
        <section className="surface-card">
          <div className="card-heading">
            <LockKeyhole size={21} />
            <h2>Change password</h2>
          </div>
          <p>
            Changing your password signs out other devices and revokes existing
            API tokens.
          </p>
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              const form = event.currentTarget;
              const data = Object.fromEntries(new FormData(form));
              if (data.password !== data.confirm) {
                setStatus("New passwords do not match.");
                return;
              }
              setBusy(true);
              try {
                const result = await api<{ detail: string }>(
                  "account/password/",
                  { method: "POST", body: JSON.stringify(data) },
                );
                form.reset();
                setDevices(await api<Device[]>("account/sessions/"));
                setStatus(result.detail);
              } catch (error) {
                setStatus((error as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            <label htmlFor="current-password">
              Current password
              <input
                id="current-password"
                name="current_password"
                type="password"
                autoComplete="current-password"
                required
                disabled={busy}
              />
            </label>
            <label htmlFor="new-password">
              New password
              <input
                id="new-password"
                name="password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                disabled={busy}
              />
            </label>
            <label htmlFor="confirm-new-password">
              Confirm new password
              <input
                id="confirm-new-password"
                name="confirm"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                disabled={busy}
              />
            </label>
            <button className="button" disabled={busy}>
              Update password
            </button>
          </form>
        </section>
        <section className="surface-card device-card">
          <div className="card-heading">
            <Monitor size={21} />
            <h2>Signed-in devices</h2>
          </div>
          <p>
            Only browser sessions started through the new sign-in flow appear
            here.
          </p>
          {devices.length ? (
            devices.map((device) => (
              <div className="device-row" key={device.id}>
                <Monitor size={20} />
                <div>
                  <strong>{device.device}</strong>
                  <small>
                    Signed in {new Date(device.created_at).toLocaleString()}
                  </small>
                </div>
                {device.current ? (
                  <span className="status-pill">This device</span>
                ) : (
                  <button
                    className="text-button"
                    disabled={busy}
                    onClick={async () => {
                      setBusy(true);
                      try {
                        await api(`account/sessions/${device.id}/`, {
                          method: "DELETE",
                        });
                        setDevices(await api<Device[]>("account/sessions/"));
                        setStatus("That device has been signed out.");
                      } catch (error) {
                        setStatus((error as Error).message);
                      } finally {
                        setBusy(false);
                      }
                    }}
                  >
                    Sign out device
                  </button>
                )}
              </div>
            ))
          ) : (
            <p>No active browser sessions to list.</p>
          )}
        </section>
      </div>
      <p className="settings-status" role="status">
        {status}
      </p>
    </section>
  );
}
