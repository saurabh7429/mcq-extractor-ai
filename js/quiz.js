/**
 * quiz.js - Quiz functionality
 */

// Get base path for redirects (works with sub-directory hosting like GitHub Pages)
const BASE_PATH = (function() {
    const path = window.location.pathname;
    if (path === '/' || path === '') return '/';
    // Remove trailing slash if present
    let base = path.endsWith('/') ? path.slice(0, -1) : path;
    // Get the repo name from the path
    const parts = base.split('/');
    // Check if the second part looks like a repo name (not a file like quiz.html)
    // Repo names typically don't have dots and are not .html files
    if (parts.length > 1 && parts[1] && !parts[1].endsWith('.html') && parts[1] !== '') {
        return '/' + parts[1] + '/';
    }
    return '/';
})();

// Quiz state
let quizQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let correctAnswers = 0;
let wrongAnswers = 0;
let isExamMode = false;
let examTimer = null;
let timeRemaining = 60; // seconds per question
let tabSwitchCount = 0;
const MAX_TAB_SWITCHES = 3;

// Original questions for restart functionality
let originalQuestions = [];

// Store options shuffle state per question to preserve selections
let questionShuffleState = {};

// DOM Elements
const questionCard = document.getElementById('questionCard');
const questionNumber = document.getElementById('questionNumber');
const questionText = document.getElementById('questionText');
const optionsList = document.getElementById('optionsList');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const quizProgressText = document.getElementById('quizProgressText');
const progressCorrect = document.getElementById('progressCorrect');
const progressWrong = document.getElementById('progressWrong');
const progressTextOverlay = document.getElementById('progressTextOverlay');
const correctCountEl = document.getElementById('correctCount');
const wrongCountEl = document.getElementById('wrongCount');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const quizTimer = document.getElementById('quizTimer');
const timerDisplay = document.getElementById('timerDisplay');
const tabWarning = document.getElementById('tabWarning');
const tabSwitchCountEl = document.getElementById('tabSwitchCount');
const resultScreen = document.getElementById('resultScreen');
const quizContainer = document.getElementById('quizContainer');

// Result elements
const resultIcon = document.getElementById('resultIcon');
const resultTitle = document.getElementById('resultTitle');
const resultMessage = document.getElementById('resultMessage');
const resultCorrect = document.getElementById('resultCorrect');
const resultWrong = document.getElementById('resultWrong');
const resultPercentage = document.getElementById('resultPercentage');
const restartSameBtn = document.getElementById('restartSameBtn');
const restartRandomBtn = document.getElementById('restartRandomBtn');
const backToPreviewBtn = document.getElementById('backToPreviewBtn');

// Initialize quiz
document.addEventListener('DOMContentLoaded', function() {
    initQuiz();
});

function initQuiz() {
    // Get quiz questions from sessionStorage
    const storedQuestions = sessionStorage.getItem('quizQuestions');
    if (!storedQuestions) {
        showError('No quiz questions found. Please go back to preview.');
        return;
    }
    
    quizQuestions = JSON.parse(storedQuestions);
    originalQuestions = JSON.parse(storedQuestions);
    
    // Store quiz type
    const quizType = sessionStorage.getItem('quizType');
    const selectedRandomCount = parseInt(sessionStorage.getItem('selectedRandomCount') || '0');
    
    if (quizQuestions.length === 0) {
        showError('No questions available for quiz.');
        return;
    }
    
    // Shuffle questions and options
    quizQuestions = shuffleQuestions(quizQuestions);
    
    // Initialize user answers array
    userAnswers = new Array(quizQuestions.length).fill(null);
    
    // Setup event listeners
    setupEventListeners();
    
    // Display first question
    displayQuestion(0);
    
    // Update progress
    updateProgress();
    
    // Apply anti-cheat measures
    applyAntiCheat();
}

function setupEventListeners() {
    // Previous button
    prevBtn.addEventListener('click', function() {
        if (currentQuestionIndex > 0) {
            displayQuestion(currentQuestionIndex - 1);
        }
    });
    
    // Next button
    nextBtn.addEventListener('click', function() {
        if (currentQuestionIndex < quizQuestions.length - 1) {
            displayQuestion(currentQuestionIndex + 1);
        } else {
            // Last question - check if all questions are answered
            const unansweredCount = userAnswers.filter(function(a) { return a === null; }).length;
            
            if (unansweredCount > 0) {
                // Show custom warning instead of confirm - don't allow finishing
                showToast('Please attempt all ' + unansweredCount + ' remaining question(s) before finishing!', 'error');
                // Navigate to first unanswered question
                const firstUnansweredIndex = userAnswers.findIndex(function(a) { return a === null; });
                displayQuestion(firstUnansweredIndex);
                return;
            }
            
            // Show results
            showResults();
        }
    });
    
    // Full screen button
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    
    // Tab visibility change (exam mode anti-cheat)
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Right-click disable
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
    
    // Keyboard shortcuts disable
    document.addEventListener('keydown', function(e) {
        // Disable Ctrl+C, Ctrl+U, Ctrl+S, F12
        if (e.ctrlKey && (e.key === 'c' || e.key === 'u' || e.key === 's')) {
            e.preventDefault();
        }
    });
    
    // Result buttons
    restartSameBtn.addEventListener('click', restartSameQuestions);
    restartRandomBtn.addEventListener('click', restartRandomQuestions);
    backToPreviewBtn.addEventListener('click', backToPreview);
}

function displayQuestion(index) {
    currentQuestionIndex = index;
    const question = quizQuestions[index];
    
    // Update question number
    questionNumber.textContent = 'Question ' + (index + 1);
    
    // Update progress text
    quizProgressText.textContent = (index + 1) + ' / ' + quizQuestions.length;
    
    // Update question text
    questionText.textContent = question.question;
    
    // Check if we already have shuffle state for this question index
    // This preserves the shuffle when going back to previous questions
    // Also preserve shuffle state if user has already answered this question
    const userHasAnswered = userAnswers[index] !== null;
    
    if (!questionShuffleState[index] || !question.shuffledOptions || !userHasAnswered) {
        // Only shuffle if user hasn't answered yet OR no shuffle state exists
        if (!questionShuffleState[index]) {
            // Shuffle options for this question
            const shuffledQuestion = shuffleOptions(question);
            
            // Store shuffled options for answer checking
            quizQuestions[index].shuffledOptions = shuffledQuestion.shuffledOptions;
            quizQuestions[index].originalCorrectIndex = question.correct_answer;
            quizQuestions[index].mappedCorrectIndex = shuffledQuestion.correctIndex;
            
            // Save shuffle state to preserve it when navigating back
            questionShuffleState[index] = {
                shuffledOptions: shuffledQuestion.shuffledOptions,
                mappedCorrectIndex: shuffledQuestion.correctIndex
            };
        } else {
            // Use existing shuffle state from previous display
            quizQuestions[index].shuffledOptions = questionShuffleState[index].shuffledOptions;
            quizQuestions[index].mappedCorrectIndex = questionShuffleState[index].mappedCorrectIndex;
        }
    } else {
        // User has already answered - ALWAYS use existing shuffle state
        quizQuestions[index].shuffledOptions = questionShuffleState[index].shuffledOptions;
        quizQuestions[index].mappedCorrectIndex = questionShuffleState[index].mappedCorrectIndex;
    }
    
    // Render options
    renderOptions(quizQuestions[index].shuffledOptions, index);
    
    // Update navigation buttons
    prevBtn.disabled = index === 0;
    
    if (index === quizQuestions.length - 1) {
        nextBtn.innerHTML = 'Finish <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
    } else {
        nextBtn.innerHTML = 'Next <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>';
    }
    
    // Restart timer for exam mode
    if (isExamMode && examTimer) {
        clearInterval(examTimer);
    }
    
    // Animate card
    questionCard.style.animation = 'none';
    questionCard.offsetHeight; // Trigger reflow
    questionCard.style.animation = 'fadeInUp 0.4s ease-out';
}

function renderOptions(options, questionIndex) {
    optionsList.innerHTML = '';
    const letters = ['A', 'B', 'C', 'D'];
    const userAnswer = userAnswers[questionIndex];
    const isAnswered = userAnswer !== null;
    
    options.forEach(function(option, idx) {
        const optionEl = document.createElement('div');
        optionEl.className = 'quiz-option';
        
        if (isAnswered) {
            optionEl.classList.add('disabled');
            
            if (idx === userAnswer) {
                // This is the user's answer
                const isCorrect = idx === quizQuestions[questionIndex].mappedCorrectIndex;
                optionEl.classList.add(isCorrect ? 'correct' : 'wrong');
                
                if (!isCorrect) {
                    optionEl.classList.add('show-correct');
                }
            } else if (idx === quizQuestions[questionIndex].mappedCorrectIndex) {
                // This is the correct answer
                optionEl.classList.add('correct');
            }
        }
        
        let iconHtml = '';
        if (isAnswered) {
            if (idx === userAnswer) {
                const isCorrect = idx === quizQuestions[questionIndex].mappedCorrectIndex;
                iconHtml = '<svg class="option-result-icon ' + (isCorrect ? 'correct' : 'wrong') + '" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">' +
                    (isCorrect ? 
                        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />' :
                        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />') +
                    '</svg>';
            } else if (idx === quizQuestions[questionIndex].mappedCorrectIndex) {
                iconHtml = '<svg class="option-result-icon correct" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">' +
                    '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
            }
        }
        
        optionEl.innerHTML = '<span class="option-letter">' + letters[idx] + '</span>' +
            '<span class="option-text">' + escapeHtml(option) + '</span>' +
            iconHtml;
        
        // Add click handler only if not answered
        if (!isAnswered) {
            optionEl.addEventListener('click', function() {
                selectOption(idx, questionIndex);
            });
        }
        
        optionsList.appendChild(optionEl);
    });
}

function selectOption(optionIndex, questionIndex) {
    // Store user's answer
    userAnswers[questionIndex] = optionIndex;
    
    // Check if correct
    const correctIndex = quizQuestions[questionIndex].mappedCorrectIndex;
    if (optionIndex === correctIndex) {
        correctAnswers++;
    } else {
        wrongAnswers++;
    }
    
    // Update progress
    updateProgress();
    
    // Re-render options to show feedback
    renderOptions(quizQuestions[questionIndex].shuffledOptions, questionIndex);
    
    // Enable next button
    nextBtn.disabled = false;
}

function updateProgress() {
    const total = quizQuestions.length;
    const answered = userAnswers.filter(function(a) { return a !== null; }).length;
    const percentage = Math.round((answered / total) * 100);
    
    // Update progress bar
    const correctPercent = (correctAnswers / total) * 100;
    const wrongPercent = (wrongAnswers / total) * 100;
    
    progressCorrect.style.width = correctPercent + '%';
    progressWrong.style.width = wrongPercent + '%';
    progressTextOverlay.textContent = percentage + '%';
    
    // Update stats
    correctCountEl.textContent = correctAnswers;
    wrongCountEl.textContent = wrongAnswers;
}

function shuffleQuestions(questions) {
    // Fisher-Yates shuffle
    var shuffled = [].concat(questions);
    for (var i = shuffled.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function shuffleOptions(question) {
    var options = [].concat(question.options);
    var correctAnswer = question.correct_answer;
    
    // Fisher-Yates shuffle
    for (var i = options.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
        
        // Update correct answer index if it was swapped
        if (correctAnswer === i) {
            correctAnswer = j;
        } else if (correctAnswer === j) {
            correctAnswer = i;
        }
    }
    
    return {
        shuffledOptions: options,
        correctIndex: correctAnswer
    };
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(function() {
            fullscreenBtn.classList.add('fullscreen');
        }).catch(function(err) {
            console.log('Fullscreen error:', err);
        });
    } else {
        document.exitFullscreen().then(function() {
            fullscreenBtn.classList.remove('fullscreen');
        }).catch(function(err) {
            console.log('Exit fullscreen error:', err);
        });
    }
}

function handleVisibilityChange() {
    if (document.hidden && isExamMode) {
        tabSwitchCount++;
        tabSwitchCountEl.textContent = tabSwitchCount;
        
        // Show warning
        tabWarning.classList.remove('hidden');
        
        if (tabSwitchCount >= MAX_TAB_SWITCHES) {
            // Auto-submit exam
            showResults();
        }
        
        // Hide warning after 3 seconds
        setTimeout(function() {
            tabWarning.classList.add('hidden');
        }, 3000);
    }
}

function applyAntiCheat() {
    // Disable right-click
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Disable text selection
    document.body.style.userSelect = 'none';
    document.body.style.webkitUserSelect = 'none';
    
    // Disable drag
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Disable long press on mobile
    document.addEventListener('touchstart', function(e) {
        if (e.touches.length > 1) {
            e.preventDefault();
        }
    }, { passive: false });
    
    var lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        var now = new Date().getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Disable copy
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Disable cut
    document.addEventListener('cut', function(e) {
        e.preventDefault();
        return false;
    });
    
    // Disable paste
    document.addEventListener('paste', function(e) {
        e.preventDefault();
        return false;
    });
}

function showResults() {
    // Stop exam timer if running
    if (examTimer) {
        clearInterval(examTimer);
    }
    
    // Exit fullscreen
    if (document.fullscreenElement) {
        document.exitFullscreen().catch(function() {});
    }
    
    // Calculate results
    const total = quizQuestions.length;
    const percentage = Math.round((correctAnswers / total) * 100);
    
    // Hide quiz container
    quizContainer.classList.add('hidden');
    
    // Show result screen
    resultScreen.classList.remove('hidden');
    
    // Set result values
    resultCorrect.textContent = correctAnswers;
    resultWrong.textContent = wrongAnswers;
    resultPercentage.textContent = percentage + '%';
    
    // Set result message based on score - 20+ compliment messages!
    var title, message, iconClass;
    
    // Score-based messages with 20+ variety
    if (percentage >= 90) {
        // Top tier - Excellent
        const excellentMessages = [
            { title: 'Excellent!', message: 'Outstanding performance! You nailed it!', icon: 'excellent' },
            { title: 'Perfect Score!', message: 'You\'re a genius! Absolutely brilliant!', icon: 'excellent' },
            { title: 'Outstanding!', message: 'Your hard work really paid off! Amazing!', icon: 'excellent' },
            { title: 'Marvelous!', message: 'You\'ve mastered this material completely!', icon: 'excellent' },
            { title: 'Spectacular!', message: 'Nothing short of perfection! Great job!', icon: 'excellent' },
            { title: 'Phenomenal!', message: 'You\'re on fire! Keep up the amazing work!', icon: 'excellent' }
        ];
        const choice = excellentMessages[Math.floor(Math.random() * excellentMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    } else if (percentage >= 80) {
        // Great tier
        const greatMessages = [
            { title: 'Great Job!', message: 'Well done! Keep up the good work!', icon: 'good' },
            { title: 'Awesome!', message: 'You\'re doing fantastic! Keep it up!', icon: 'good' },
            { title: 'Superb!', message: 'Excellent effort! You\'re crushing it!', icon: 'good' },
            { title: 'Impressive!', message: 'You\'re really excelling! Well deserved!', icon: 'good' },
            { title: 'Terrific!', message: 'Amazing work! You\'re a star!', icon: 'good' }
        ];
        const choice = greatMessages[Math.floor(Math.random() * greatMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    } else if (percentage >= 70) {
        // Good tier
        const goodMessages = [
            { title: 'Good Work!', message: 'Nice job! You\'re on the right track!', icon: 'good' },
            { title: 'Well Done!', message: 'You\'re making great progress!', icon: 'good' },
            { title: 'Nice Work!', message: 'Keep pushing forward! You\'re improving!', icon: 'good' },
            { title: 'Great Effort!', message: 'You\'re doing really well! Stay focused!', icon: 'good' },
            { title: 'Thumbs Up!', message: 'You\'re getting there! Keep it going!', icon: 'good' }
        ];
        const choice = goodMessages[Math.floor(Math.random() * goodMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    } else if (percentage >= 60) {
        // Average tier - Not bad
        const notBadMessages = [
            { title: 'Not Bad!', message: 'Good effort! A little more practice will help.', icon: 'average' },
            { title: 'Decent Job!', message: 'You\'re getting there! Keep practicing!', icon: 'average' },
            { title: 'Nice Try!', message: 'You\'re improving! Don\'t give up!', icon: 'average' },
            { title: 'Good Try!', message: 'Almost there! A bit more effort will get you there!', icon: 'average' },
            { title: 'Keep Going!', message: 'You\'re making progress! Stay determined!', icon: 'average' }
        ];
        const choice = notBadMessages[Math.floor(Math.random() * notBadMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    } else if (percentage >= 50) {
        // Fair tier
        const fairMessages = [
            { title: 'Fair Attempt', message: 'You\'re halfway there! Keep practicing!', icon: 'average' },
            { title: 'Not Bad!', message: 'You\'re improving! Review and try again!', icon: 'average' },
            { title: 'Keep Trying!', message: 'You can do better! Don\'t stop now!', icon: 'average' },
            { title: 'Almost There!', message: 'Just a little more practice needed!', icon: 'average' },
            { title: 'Good Start!', message: 'You\'re building a foundation! Keep learning!', icon: 'average' }
        ];
        const choice = fairMessages[Math.floor(Math.random() * fairMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    } else {
        // Below 50% - Keep practicing
        const practiceMessages = [
            { title: 'Keep Practicing!', message: 'Don\'t give up! Review the material and try again.', icon: 'poor' },
            { title: 'Don\'t Give Up!', message: 'Every expert was once a beginner. Keep trying!', icon: 'poor' },
            { title: 'Stay Positive!', message: 'Practice makes perfect. You\'ll get there!', icon: 'poor' },
            { title: 'Keep Learning!', message: 'Review your weak areas and try again!', icon: 'poor' },
            { title: 'Never Give Up!', message: 'Success is just around the corner. Keep going!', icon: 'poor' },
            { title: 'You Can Do It!', message: 'Believe in yourself and keep practicing!', icon: 'poor' }
        ];
        const choice = practiceMessages[Math.floor(Math.random() * practiceMessages.length)];
        title = choice.title;
        message = choice.message;
        iconClass = choice.icon;
    }
    
    resultTitle.textContent = title;
    resultMessage.textContent = message;
    
    // Set icon
    resultIcon.className = 'result-icon ' + iconClass;
    resultIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">' +
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />' +
        '</svg>';
}

function restartSameQuestions() {
    // Reset state
    currentQuestionIndex = 0;
    userAnswers = new Array(quizQuestions.length).fill(null);
    correctAnswers = 0;
    wrongAnswers = 0;
    tabSwitchCount = 0;
    
    // Use same questions (shuffle options again)
    quizQuestions = shuffleQuestions(quizQuestions);
    quizQuestions.forEach(function(q) {
        var shuffled = shuffleOptions(q);
        q.shuffledOptions = shuffled.shuffledOptions;
        q.mappedCorrectIndex = shuffled.correctIndex;
    });
    
    // Show quiz container
    resultScreen.classList.add('hidden');
    quizContainer.classList.remove('hidden');
    
    // Display first question
    displayQuestion(0);
    updateProgress();
}

function restartRandomQuestions() {
    // Reset state
    currentQuestionIndex = 0;
    userAnswers = new Array(originalQuestions.length).fill(null);
    correctAnswers = 0;
    wrongAnswers = 0;
    tabSwitchCount = 0;
    
    // Get new random questions from original
    quizQuestions = shuffleQuestions([].concat(originalQuestions));
    
    // Store in session
    sessionStorage.setItem('quizQuestions', JSON.stringify(quizQuestions));
    
    // Show quiz container
    resultScreen.classList.add('hidden');
    quizContainer.classList.remove('hidden');
    
    // Display first question
    displayQuestion(0);
    updateProgress();
}

function backToPreview() {
    // Clear quiz data
    sessionStorage.removeItem('quizQuestions');
    sessionStorage.removeItem('quizType');
    sessionStorage.removeItem('selectedRandomCount');
    
    // Use BASE_PATH for redirect (works with subdirectory hosting like GitHub Pages)
    window.location.href = BASE_PATH + 'preview.html';
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    var errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = 'position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: var(--bg-primary); z-index: 9999;';
    errorDiv.innerHTML = '<div style="text-align: center; padding: 2rem;">' +
        '<h2 style="color: var(--danger); margin-bottom: 1rem;">Error</h2>' +
        '<p style="color: var(--text-secondary);">' + message + '</p>' +
        '<button onclick="window.location.href=\'preview.html\'" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">Go to Preview</button>' +
        '</div>';
    document.body.appendChild(errorDiv);
}

function showToast(message, type) {
    // Create toast container if not exists
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container';
        toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.style.cssText = 'background: ' + (type === 'error' ? '#ef4444' : '#10b981') + '; color: white; padding: 12px 20px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); animation: slideIn 0.3s ease-out;';
    
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = '<svg style="width: 20px; height: 20px; margin-right: 8px; vertical-align: middle;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
    } else if (type === 'error') {
        iconSvg = '<svg style="width: 20px; height: 20px; margin-right: 8px; vertical-align: middle;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
    }
    
    toast.innerHTML = iconSvg + '<span style="vertical-align: middle;">' + escapeHtml(message) + '</span>';
    toastContainer.appendChild(toast);
    
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease-out';
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

// Export functions for debugging
window.Quiz = {
    displayQuestion: displayQuestion,
    selectOption: selectOption,
    showResults: showResults
};

