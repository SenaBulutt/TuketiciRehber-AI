const chatForm =
    document.getElementById("chatForm");

const questionInput =
    document.getElementById("questionInput");

const chatArea =
    document.getElementById("chatArea");

const sendButton =
    document.getElementById("sendButton");

const welcomeSection =
    document.getElementById("welcomeSection");

const newChatButton =
    document.getElementById("newChatButton");

const refreshHistoryButton =
    document.getElementById("refreshHistoryButton");

const starterCards =
    document.querySelectorAll(".starter-card");


function escapeHtml(text) {
    const div =
        document.createElement("div");

    div.textContent = text ?? "";

    return div.innerHTML;
}


function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
    });
}


function addUserMessage(question) {
    const row =
        document.createElement("div");

    row.className =
        "message-row user";

    row.innerHTML = `
        <div class="user-message">
            ${escapeHtml(question)}
        </div>
    `;

    chatArea.appendChild(row);
}


function kaynakHtmlOlustur(kaynaklar) {

    if (
        !kaynaklar ||
        kaynaklar.length === 0
    ) {
        return "";
    }

    const sourceTags =
        kaynaklar.map(source => `
            <div class="source-tag">

                ▤ ${escapeHtml(source.ad)}

                <strong>
                    Resmî kaynak
                </strong>

            </div>
        `).join("");

    return `
        <div class="sources-block">

            <div class="sources-label">
                KULLANILAN KAYNAKLAR
            </div>

            <div class="source-tags">
                ${sourceTags}
            </div>

        </div>
    `;
}


function addAssistantMessage(data) {

    const row =
        document.createElement("div");

    row.className =
        "message-row assistant";

    row.innerHTML = `
        <div class="assistant-message">

            <div class="assistant-title">
                TüketiciRehber AI
            </div>

            <div class="assistant-answer">
                ${escapeHtml(data.cevap)}
            </div>

            ${kaynakHtmlOlustur(
                data.kaynaklar
            )}

        </div>
    `;

    chatArea.appendChild(row);
}


function addLoadingMessage() {

    const row =
        document.createElement("div");

    row.className =
        "message-row assistant";

    row.id =
        "loadingMessage";

    row.innerHTML = `
        <div class="assistant-message">

            <div class="assistant-title">
                TüketiciRehber AI
            </div>

            <div class="loading-message">

                Resmî kaynaklar inceleniyor

                <span class="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                </span>

            </div>

        </div>
    `;

    chatArea.appendChild(row);
}


function removeLoadingMessage() {

    const loading =
        document.getElementById(
            "loadingMessage"
        );

    if (loading) {
        loading.remove();
    }
}


function addErrorMessage(message) {

    const row =
        document.createElement("div");

    row.className =
        "message-row assistant";

    row.innerHTML = `
        <div class="assistant-message">

            <div class="assistant-title">
                TüketiciRehber AI
            </div>

            <div class="assistant-answer">
                ${escapeHtml(message)}
            </div>

        </div>
    `;

    chatArea.appendChild(row);
}


async function askQuestion(question) {

    question =
        question.trim();

    if (!question) {
        return;
    }

    if (welcomeSection) {
        welcomeSection.style.display =
            "none";
    }

    addUserMessage(question);

    questionInput.value = "";

    questionInput.disabled = true;
    sendButton.disabled = true;

    addLoadingMessage();

    scrollToBottom();

    try {

        const response =
            await fetch(
                "/api/sor",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            soru: question
                        })
                }
            );

        const data =
            await response.json();

        removeLoadingMessage();

        if (!response.ok) {

            addErrorMessage(
                data.hata ||
                "Bir hata oluştu."
            );

        } else {

            addAssistantMessage(data);

            await sohbetGecmisiniYukle();
        }

    } catch (error) {

        console.error(error);

        removeLoadingMessage();

        addErrorMessage(
            "Sunucuya bağlanılamadı. Lütfen tekrar deneyin."
        );

    } finally {

        questionInput.disabled = false;
        sendButton.disabled = false;

        questionInput.focus();

        scrollToBottom();
    }
}


function tarihDuzenle(tarih) {

    if (!tarih) {
        return "";
    }

    const sqliteTarih =
        tarih.replace(" ", "T") + "Z";

    const date =
        new Date(sqliteTarih);

    return date.toLocaleString(
        "tr-TR",
        {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


async function sohbetGecmisiniYukle() {

    const alan =
        document.getElementById(
            "sohbet-gecmisi"
        );

    if (!alan) {
        return;
    }

    try {

        const response =
            await fetch(
                "/api/gecmis"
            );

        if (!response.ok) {
            throw new Error(
                "Geçmiş alınamadı."
            );
        }

        const sohbetler =
            await response.json();

        alan.innerHTML = "";

        if (
            sohbetler.length === 0
        ) {

            alan.innerHTML = `
                <div class="history-empty">
                    Henüz sohbet bulunmuyor.
                </div>
            `;

            return;
        }


        sohbetler.forEach(
            sohbet => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "history-item";


                const main =
                    document.createElement(
                        "div"
                    );

                main.className =
                    "history-main";


                main.innerHTML = `
                    <div class="history-question">
                        ${escapeHtml(
                            sohbet.soru
                        )}
                    </div>

                    <div class="history-date">
                        ${escapeHtml(
                            tarihDuzenle(
                                sohbet.tarih
                            )
                        )}
                    </div>
                `;


                main.addEventListener(
                    "click",
                    () => {
                        gecmisSohbetiGoster(
                            sohbet
                        );
                    }
                );


                const deleteButton =
                    document.createElement(
                        "button"
                    );

                deleteButton.className =
                    "history-delete";

                deleteButton.type =
                    "button";

                deleteButton.innerHTML = "Sil";


                deleteButton.addEventListener(
                    "click",
                    async event => {

                        event.stopPropagation();

                        await sohbetSil(
                            sohbet.id
                        );
                    }
                );


                item.appendChild(main);

                item.appendChild(
                    deleteButton
                );

                alan.appendChild(item);
            }
        );

    } catch (error) {

        console.error(error);

        alan.innerHTML = `
            <div class="history-empty">
                Sohbet geçmişi yüklenemedi.
            </div>
        `;
    }
}


let silinecekSohbetId = null;


function sohbetSil(id) {

    silinecekSohbetId = id;

    const modal =
        document.getElementById("deleteModal");

    modal.classList.add("show");
}


function silmeModaliniKapat() {

    const modal =
        document.getElementById("deleteModal");

    modal.classList.remove("show");

    silinecekSohbetId = null;
}


document
    .getElementById("cancelDeleteButton")
    .addEventListener("click", () => {

        silmeModaliniKapat();

    });


document
    .getElementById("confirmDeleteButton")
    .addEventListener("click", async () => {

        if (!silinecekSohbetId) {
            return;
        }

        const id = silinecekSohbetId;

        try {

            const response = await fetch(
                `/api/gecmis/${id}`,
                {
                    method: "DELETE"
                }
            );

            if (!response.ok) {
                throw new Error("Sohbet silinemedi.");
            }

            silmeModaliniKapat();

            await sohbetGecmisiniYukle();

        } catch (error) {

            console.error(error);

            alert("Sohbet silinirken bir hata oluştu.");
        }

    });


document
    .getElementById("deleteModal")
    .addEventListener("click", event => {

        if (event.target.id === "deleteModal") {
            silmeModaliniKapat();
        }

    });


function gecmisSohbetiGoster(
    sohbet
) {

    if (welcomeSection) {
        welcomeSection.style.display =
            "none";
    }

    chatArea.innerHTML = "";

    addUserMessage(
        sohbet.soru
    );

    addAssistantMessage({
        cevap:
            sohbet.cevap,

        kaynaklar:
            sohbet.kaynaklar || []
    });

    scrollToBottom();
}


function yeniSohbetBaslat() {

    chatArea.innerHTML = "";

    if (welcomeSection) {
        welcomeSection.style.display =
            "";
    }

    questionInput.value = "";

    questionInput.focus();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


chatForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();

        askQuestion(
            questionInput.value
        );
    }
);


starterCards.forEach(
    card => {

        card.addEventListener(
            "click",
            () => {

                askQuestion(
                    card.dataset.question
                );
            }
        );
    }
);


if (newChatButton) {

    newChatButton.addEventListener(
        "click",
        yeniSohbetBaslat
    );
}


if (refreshHistoryButton) {

    refreshHistoryButton.addEventListener(
        "click",
        sohbetGecmisiniYukle
    );
}


document.addEventListener(
    "DOMContentLoaded",
    sohbetGecmisiniYukle
);