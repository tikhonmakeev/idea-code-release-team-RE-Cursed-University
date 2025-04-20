import { useState, useRef, useEffect } from "react";
import "./style.css";

const encodeCredentials = (username, password) => {
  return btoa(unescape(encodeURIComponent(`${username}:${password}`)));
};

const AuthPopup = ({ onClose, onAuthSuccess }) => {
  const [authMode, setAuthMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const popupRef = useRef(null);
  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError("");

    const endpoint =
      authMode === "register"
        ? `${apiUrl}/auth/register`
        : `${apiUrl}/auth/get_my_info`;
    const credentials = encodeCredentials(username, password);

    try {
      let method = "POST";
      let body = JSON.stringify({
        login: username,
        password: password,
      });
      if (authMode === "login") {
        method = "GET";
        body = null;
      }
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          Authorization: `Basic ${credentials}`,
          "Content-Type": "application/json",
        },
        body: body
      });

      if (!response.ok) {
        throw new Error(
          authMode === "login"
            ? "Неверные логин или пароль"
            : "Регистрация не удалась"
        );
      }

      onAuthSuccess(credentials);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="popup__overlay">
      <div className="popup" ref={popupRef}>
        <img src="../../../public/ico.png" alt="Лого" className="popup__img" />
        <h2 className="popup__title">
          {authMode === "login" ? "Вход" : "Регистрация"}
        </h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleAuth}>
          <input
            type="text"
            placeholder="Логин"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="popup__input"
          />
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="popup__input"
          />
          <div className="popup__btns">
            <button type="submit" className="popup__btn primary">
              {authMode === "login" ? "Войти" : "Зарегистрироваться"}
            </button>
            <button
              type="button"
              className="popup__btn secondary"
              onClick={() =>
                setAuthMode(authMode === "login" ? "register" : "login")
              }
            >
              {authMode === "login" ? "Регистрация" : "Вход"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthPopup;
