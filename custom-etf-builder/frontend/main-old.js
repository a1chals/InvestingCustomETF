// Global variables
let chart;
let userInputText = '';

// Interface elements
const mainInterface = document.getElementById('main-interface');
const optionsInterface = document.getElementById('options-interface');
const loadingInterface = document.getElementById('loading-interface');
const resultsInterface = document.getElementById('results-interface');
const errorDisplay = document.getElementById('error');

// Form elements
const portfolioForm = document.getElementById('portfolio-form');
const textInput = document.getElementById('text');
const generateButton = document.getElementById('generate-portfolio');
const backToMainButton = document.getElementById('back-to-main');
const startOverButton = document.getElementById('start-over');
const errorRetryButton = document.getElementById('error-retry');

// Results elements
const table = document.getElementById('table');
const riskProfile = document.getElementById('risk-profile');
const asOf = document.getElementById('as-of');
const themes = document.getElementById('themes');

// Utility functions
function showInterface(interfaceToShow) {
  [mainInterface, optionsInterface, loadingInterface, resultsInterface, errorDisplay].forEach(el => {
    if (el) el.style.display = 'none';
  });
  if (interfaceToShow) interfaceToShow.style.display = 'flex';
}

function showError(message) {
  const errorMessage = document.getElementById('error-message');
  if (errorMessage) errorMessage.textContent = message;
  showInterface(errorDisplay);
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

// Chart rendering
function renderPie(canvasId, holdings, amount) {
  const ctx = document.getElementById(canvasId);
  const labels = holdings.map(h => h.symbol);
  const data = holdings.map(h => Math.round(h.weight * 100));
  
  // Beautiful gradient colors inspired by the modern design
  const colors = [
    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe',
    '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
  ];
  
  if (chart) chart.destroy();
  
  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.slice(0, holdings.length),
        borderWidth: 0,
        hoverBorderWidth: 3,
        hoverBorderColor: 'rgba(255, 255, 255, 0.8)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      animation: {
        animateScale: true,
        animateRotate: true,
        duration: 1500,
        easing: 'easeOutQuart'
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#1f2937',
          bodyColor: '#1f2937',
          borderColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          cornerRadius: 12,
          callbacks: {
            label: function(context) {
              const percentage = context.parsed;
              const value = formatCurrency((percentage / 100) * amount);
              return `${context.label}: ${percentage}% (${value})`;
            }
          }
        }
      }
    }
  });
}

// Table rendering
function renderTable(holdings, amount) {
  const tbody = table.querySelector('tbody');
  tbody.innerHTML = '';
  
  holdings.forEach(holding => {
    const tr = document.createElement('tr');
    const dollarAmount = formatCurrency(holding.weight * amount);
    const weightPercentage = (holding.weight * 100).toFixed(1);
    
    tr.innerHTML = `
      <td><strong>${holding.symbol}</strong></td>
      <td>${weightPercentage}%</td>
      <td>${dollarAmount}</td>
      <td>${holding.rationale || 'Investment rationale not available'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Results rendering
function renderResults(data, amount, risk) {
  renderPie('pie', data.holdings || [], amount);
  renderTable(data.holdings || [], amount);
  
  riskProfile.textContent = risk.charAt(0).toUpperCase() + risk.slice(1);
  asOf.textContent = new Date().toLocaleDateString();
  
  if (Array.isArray(data.themes_detected) && data.themes_detected.length > 0) {
    themes.textContent = data.themes_detected.map(theme => 
      typeof theme === 'string' ? theme : 
      typeof theme === 'object' ? theme.theme : 
      String(theme)
    ).join(', ');
  } else {
    themes.textContent = 'Market Analysis';
  }
}

// Event handlers
portfolioForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  userInputText = textInput.value.trim();
  if (userInputText) {
    document.getElementById('user-input-display').textContent = `"${userInputText}"`;
    showInterface(optionsInterface);
  }
});

// Suggestion chips
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const text = chip.getAttribute('data-text');
    textInput.value = text;
    userInputText = text;
    document.getElementById('user-input-display').textContent = `"${text}"`;
    showInterface(optionsInterface);
  });
});

// Amount selection
document.querySelectorAll('.amount-option').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.amount-option').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    const customInput = document.getElementById('custom-amount');
    if (button.classList.contains('custom-amount-btn')) {
      customInput.style.display = 'block';
      customInput.focus();
    } else {
      customInput.style.display = 'none';
    }
  });
});

// Custom amount input
document.getElementById('custom-amount').addEventListener('input', (e) => {
  const value = e.target.value;
  if (value && !isNaN(value)) {
    document.querySelectorAll('.amount-option').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.custom-amount-btn').classList.add('active');
  }
});

// Generate portfolio
generateButton.addEventListener('click', async () => {
  const selectedRisk = document.querySelector('input[name="risk"]:checked');
  const selectedAmount = document.querySelector('.amount-option.active');
  const customAmount = document.getElementById('custom-amount');
  
  if (!selectedRisk) {
    alert('Please select a risk level');
    return;
  }
  
  if (!selectedAmount) {
    alert('Please select an investment amount');
    return;
  }
  
  let amount;
  if (selectedAmount.classList.contains('custom-amount-btn')) {
    amount = parseFloat(customAmount.value);
    if (!amount || amount <= 0) {
      alert('Please enter a valid custom amount');
      return;
    }
  } else {
    amount = parseFloat(selectedAmount.getAttribute('data-amount'));
  }
  
  const risk = selectedRisk.value;
  
  showInterface(loadingInterface);
  
  try {
    const response = await fetch('http://localhost:8000/generate_portfolio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: userInputText,
        risk: risk,
        amount: amount
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Portfolio data received:', data);
    
    renderResults(data, amount, risk);
    showInterface(resultsInterface);
    
  } catch (error) {
    console.error('Error generating portfolio:', error);
    showError('Failed to generate portfolio. Please try again.');
  }
});

// Navigation
backToMainButton.addEventListener('click', () => {
  showInterface(mainInterface);
});

startOverButton.addEventListener('click', () => {
  if (chart) {
    chart.destroy();
    chart = null;
  }
  
  textInput.value = '';
  userInputText = '';
  document.querySelectorAll('.amount-option').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('input[name="risk"]').forEach(input => input.checked = false);
  document.querySelector('input[name="risk"][value="medium"]').checked = true;
  document.getElementById('custom-amount').style.display = 'none';
  
  showInterface(mainInterface);
});

errorRetryButton.addEventListener('click', () => {
  showInterface(optionsInterface);
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  showInterface(mainInterface);
  
  const defaultRisk = document.querySelector('input[name="risk"][value="medium"]');
  if (defaultRisk) defaultRisk.checked = true;
});

// Interactive effects
document.querySelectorAll('.chip, .risk-card, .amount-option').forEach(element => {
  element.addEventListener('mouseenter', () => {
    element.style.transform = 'translateY(-2px)';
  });
  
  element.addEventListener('mouseleave', () => {
    element.style.transform = 'translateY(0)';
  });
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target === textInput) {
    portfolioForm.dispatchEvent(new Event('submit'));
  }
  
  if (e.key === 'Escape') {
    if (resultsInterface.style.display === 'flex') {
      startOverButton.click();
    } else if (optionsInterface.style.display === 'flex') {
      backToMainButton.click();
    }
  }
});
