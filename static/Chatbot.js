/* ---------- Helper Functions ---------- */

function addMessage(text, type = 'bot') {
    const chat = document.getElementById('chat');
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.innerHTML = text.replace(/\n/g, '<br>');
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

/* ---------- Input Control ---------- */

function showInput(placeholder, callback, disabled = false) {
    const area = document.querySelector('.input-area');
    area.innerHTML = `
        <input id="user-input" placeholder="${placeholder}" ${disabled ? 'disabled' : ''}>
        <button ${disabled ? 'disabled' : ''}>Send</button>
    `;

    const input = document.getElementById('user-input');
    const button = area.querySelector('button');

    input.focus();

    if (disabled) return;

    button.onclick = () => {
        const value = input.value.trim();
        if (!value) return;
        addMessage(value, 'user');
        callback(value);
        input.value = '';
    };

    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') button.click();
    });
}

/* ---------- Options (Buttons) ---------- */

function showOptions(options, callback) {
    const chat = document.getElementById('chat');

    const msg = document.createElement('div');
    msg.className = 'message bot option-message';

    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'chat-options';

    let selected = false;

    options.forEach((text, i) => {
        const btn = document.createElement('button');
        btn.className = 'chat-option-btn';
        btn.textContent = text;

        btn.onclick = () => {
            if (selected) return;
            selected = true;

            // Disable all buttons immediately
            optionsDiv.querySelectorAll('button').forEach(b => b.disabled = true);

            addMessage(text, 'user');
            callback(i + 1);
        };

        optionsDiv.appendChild(btn);
    });

    msg.appendChild(optionsDiv);
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;

    // Show input box but lock typing
    showInput("Please select an option above", () => {}, true);
}

function showError(msg) {
    addMessage(msg, 'error');
}

/* ---------- Conversation Flow ---------- */

function startChat() {
    addMessage(
        "Welcome to KKMJP Superagent. I’m Lulu, and I’ll guide you through Perlindungan Combo Insurance.<br>May I know your name?"
    );
    showInput("Enter your name", submitName);
}

async function submitName(name) {
    const res = await fetch('/submit_name', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name })
    });

    const data = await res.json();
    if (data.error) return showError(data.error);

    addMessage(data.message);
    showInput("DD/MM/YYYY", submitDob);
}

async function submitDob(dob) {
    const res = await fetch('/submit_dob', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ dob })
    });

    const data = await res.json();
    if (data.error) return showError(data.error);

    if (data.blocked) {
        addMessage(data.message);
        document.querySelector('.input-area').innerHTML =
            "<button onclick='restartChat()'>Restart Again</button>";
        return;
    }

    addMessage(data.message);

    showOptions([
        "No coverage at all",
        "Basic employee coverage",
        "Some personal coverage",
        "Comprehensive coverage"
    ], selectInsurance);
}

async function selectInsurance(level) {
    const res = await fetch('/select_insurance', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ insurance: level })
    });

    const data = await res.json();
    addMessage(data.message);

    showOptions(["3 months", "6 months", "9 months", "12 months"], selectTiming);
}

async function selectTiming(level) {
    const res = await fetch('/select_timing', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ timing: level })
    });

    const data = await res.json();
    addMessage(data.message);

    showOptions([
        "Less than RM 20,000",
        "RM 20,001 - RM 40,000",
        "RM 40,001 - RM 60,000",
        "More than RM 60,000"
    ], selectIncome);
}

async function selectIncome(level) {
    const res = await fetch('/select_income', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ income: level })
    });

    const data = await res.json();
    addMessage(data.message);

    showInput("Enter phone number", submitPhone);
}

/* ---------- Phone & Plan Selection ---------- */

async function submitPhone(phone) {
    const res = await fetch('/submit_phone', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone })
    });

    const data = await res.json();
    if (data.error) return showError(data.error);

    addMessage(data.message);

    setTimeout(() => {
        addMessage("May I know which level of protection do you want?");
        showOptions(["Standard", "Basic", "Comprehensive"], selectPreference);
    }, 600);
}

/* ---------- Plan Breakdown ---------- */

async function selectPreference(level) {
    const res = await fetch('/select_preference', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ level })
    });

    const data = await res.json();
    sessionStorage.setItem('plan', data.plan);

    addMessage(
        `Nice choice! The <b>${data.plan}</b> plan helps support your health and peace of mind.`
    );

    setTimeout(() => {
        addMessage(
            `<b>Your estimated monthly premium is RM ${data.premium}</b><br><br>` +
            `• Life: RM ${data.life}<br>` +
            `• Critical Illness: RM ${data.critical}<br>` +
            `• Medical Card: RM ${data.medical}`
        );
    }, 500);

    setTimeout(() => {
        addMessage(
            "Please type your email address, we will send you an email summary of our conversation for your reference."
        );
        showInput("Enter your email", submitEmail);
    }, 1000);
}

async function submitEmail(email) {
    const res = await fetch('/submit_email', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email })
    });

    const data = await res.json();
    if (data.error) return showError(data.error);

    addMessage(data.message);
    showOptions(["Yes", "No"], selectSignup);
}

async function selectSignup(level) {
    const interested = level === 1;

    const res = await fetch('/select_signup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ interested })
    });

    const data = await res.json();

    addMessage(
        "Great! Thank you for signing up. We will contact you soon.<br>" +
        "<i>Subject to terms and conditions of approved policy after recommendation by authorised representatives.</i>"
    );

    addMessage(data.message);

    document.querySelector('.input-area').innerHTML =
        "<button onclick='restartChat()'>Restart Again</button>";
}

function restartChat() {
    document.getElementById('chat').innerHTML = '';
    startChat();
}

document.addEventListener('DOMContentLoaded', startChat);
