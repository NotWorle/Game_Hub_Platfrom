const apiUrl = "http://your-domain.com/API/game/";

const data = {
    games: 2,  // ID game (game_id)
    users: 1,  // ID user (user_id)
    score: 150,  // Điểm số của người chơi
};

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Kích thước canvas
const canvasWidth = canvas.width;
const canvasHeight = canvas.height;

// Giỏ
const basket = {
    x: canvasWidth / 2 - 50,
    y: canvasHeight - 30,
    width: 100,
    height: 20,
    color: "brown",
    speed: 20,
};

// Bóng
let ball = {
    x: Math.random() * (canvasWidth - 20) + 10,
    y: 0,
    radius: 10,
    color: "red",
    speed: 3,
};

// Điểm số
let score = 0;

// Vẽ giỏ
function drawBasket() {
    ctx.fillStyle = basket.color;
    ctx.fillRect(basket.x, basket.y, basket.width, basket.height);
}

// Vẽ bóng
function drawBall() {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = ball.color;
    ctx.fill();
    ctx.closePath();
}

// Vẽ điểm số
function drawScore() {
    ctx.font = "20px Arial";
    ctx.fillStyle = "#000";
    ctx.fillText(`Score: ${score}`, 10, 30);
}

// Di chuyển giỏ
document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" && basket.x > 0) {
        basket.x -= basket.speed;
    } else if (event.key === "ArrowRight" && basket.x < canvasWidth - basket.width) {
        basket.x += basket.speed;
    }
});

// Cập nhật bóng
function updateBall() {
    ball.y += ball.speed;

    // Nếu bóng chạm đáy mà không được bắt
    if (ball.y > canvasHeight) {
        fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  // Định dạng dữ liệu gửi
               
            },
            body: JSON.stringify(data), // Chuyển object `data` thành JSON string
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(responseData => {
                console.log("Điểm đã được ghi nhận:", responseData);
            })
            .catch(error => {
                console.error("Có lỗi xảy ra:", error);
            });
        document.location.reload(); // Tải lại trang để chơi lại
    }

    // Kiểm tra va chạm với giỏ
    if (
        ball.y + ball.radius > basket.y &&
        ball.x > basket.x &&
        ball.x < basket.x + basket.width
    ) {
        score++;
        ball.y = 0;
        ball.x = Math.random() * (canvasWidth - 20) + 10;
        ball.speed += 0.5; // Tăng tốc độ bóng
    }
}

// Vòng lặp trò chơi
function gameLoop() {
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    drawBasket();
    drawBall();
    drawScore();

    updateBall();

    requestAnimationFrame(gameLoop);
}

// Bắt đầu trò chơi
gameLoop();
