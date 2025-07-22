// 通用的工具函数

// 显示消息通知
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 收藏题目
async function favoriteQuestion(questionId, source) {
    try {
        const response = await fetch('/student/favorite_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question_id: questionId,
                source: source
            })
        });
        
        const result = await response.json();
        if (response.ok) {
            showNotification('题目收藏成功');
            return result;
        } else {
            throw new Error(result.error || '收藏失败');
        }
    } catch (error) {
        showNotification(error.message, 'error');
        console.error('收藏题目失败:', error);
    }
}

// 获取收藏列表
async function getFavoriteQuestions() {
    try {
        const response = await fetch('/student/favorite_questions');
        const result = await response.json();
        if (response.ok) {
            return result.favorites;
        } else {
            throw new Error(result.error || '获取收藏列表失败');
        }
    } catch (error) {
        showNotification(error.message, 'error');
        console.error('获取收藏列表失败:', error);
        return [];
    }
}

// 删除收藏
async function deleteFavoriteQuestion(favoriteId) {
    try {
        const response = await fetch('/student/delete_favorite_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                favorite_id: favoriteId
            })
        });
        
        const result = await response.json();
        if (response.ok) {
            showNotification('题目已从收藏中移除');
            return result;
        } else {
            throw new Error(result.error || '删除收藏失败');
        }
    } catch (error) {
        showNotification(error.message, 'error');
        console.error('删除收藏失败:', error);
    }
}

// 显示收藏管理界面
async function showFavorites() {
    try {
        const favoritesSection = document.getElementById('favoritesSection');
        const favoritesContainer = document.getElementById('favoritesContainer');
        
        // 显示收藏区域
        favoritesSection.style.display = 'block';
        
        const favorites = await getFavoriteQuestions();
        
        if (favorites.length === 0) {
            favoritesContainer.innerHTML = '<p>暂无收藏题目</p>';
            return;
        }
        
        let html = '<div class="favorites-list">';
        favorites.forEach(fav => {
            html += `
                <div class="favorite-item" data-id="${fav.id}">
                    <div class="question">${fav.question}</div>
                    <div class="answer">${fav.answer || '暂无答案'}</div>
                    <div class="source">来源: ${fav.source === 'practice' ? '练习' : '考核'}</div>
                    <button onclick="deleteFavoriteQuestion('${fav.id}')" class="btn-delete">删除</button>
                </div>
            `;
        });
        html += '</div>';
        
        favoritesContainer.innerHTML = html;
        
        // 滚动到收藏区域
        favoritesSection.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('显示收藏列表失败:', error);
        showNotification('加载收藏列表失败: ' + error.message, 'error');
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 初始化收藏管理界面
    if (document.getElementById('favoritesContainer')) {
        showFavorites();
    }
});
