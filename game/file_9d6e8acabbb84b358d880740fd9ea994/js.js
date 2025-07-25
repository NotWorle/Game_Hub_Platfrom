async function getCSRFToken() {
    let tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput) {
        return tokenInput.value;  // Lấy từ form nếu có
    }

    // Nếu không tìm thấy trong form, lấy từ cookie
    let cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : null;
}

async function submitScore(gameId, score) {
    let csrfToken = await getCSRFToken();  // Đảm bảo có CSRF token

    try {
        const response = await fetch("http://127.0.0.1:8000/games/API/leaderboard/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,  // Gửi CSRF token
            },
            body: JSON.stringify({
                games: gameId,
                score: score,
            }),
            credentials: "include",  // Cho phép gửi cookie trong request
        });

        const data = await response.json();
        if (response.ok) {
            console.log("✅ Score submitted:", data);
        } else {
            console.error("❌ Error submitting score:", data);
        }
    } catch (error) {
        console.error("❌ Network error:", error);
    }
}

// Gọi API
submitScore(115,12311145);