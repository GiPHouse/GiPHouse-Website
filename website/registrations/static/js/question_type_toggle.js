document.addEventListener("DOMContentLoaded", () => {
    function validateRow(questionTbody) {
        const questionType = questionTbody.querySelector("select[name$='-question_type']")?.value;
        const choicesPanel = questionTbody.querySelector("tr.djn-tr:not(.form-row)");

        const isMulti = questionType === "multi";
        const isChoice = questionType === "choice";

        [
            questionTbody.querySelector("td.field-min_choices"),
            questionTbody.querySelector("td.field-max_choices"),
            questionTbody.querySelector("td.field-warnings"),
        ].forEach(td => {
            if (td) td.style.visibility = isMulti ? "visible" : "hidden";
        });

        if (choicesPanel) {
            choicesPanel.style.display = (isMulti || isChoice) ? "" : "none";
        }
    }

    function getQuestionTbody(el) {
        const tbody = el.closest("tbody[id^='question_set-']");
        if (!tbody || tbody.id.includes("choices") || tbody.id.includes("empty")) return null;
        return tbody;
    }

    function attachListeners() {
        document.querySelectorAll("select[name$='-question_type']").forEach(el => {
            if (el.dataset.warningListenerAttached) return;
            el.dataset.warningListenerAttached = "true";
            el.addEventListener("change", () => {
                const tbody = getQuestionTbody(el);
                if (tbody) validateRow(tbody);
            });
        });
    }

    function initAll() {
        document.querySelectorAll("tbody[id^='question_set-']").forEach(tbody => {
            if (!tbody.id.includes("choices") && !tbody.id.includes("empty")) {
                validateRow(tbody);
            }
        });
        attachListeners();
    }

    const observer = new MutationObserver(() => {
        attachListeners();
        document.querySelectorAll("tbody[id^='question_set-']").forEach(tbody => {
            if (!tbody.id.includes("choices") && !tbody.id.includes("empty")) {
                if (!tbody.dataset.initialized) {
                    tbody.dataset.initialized = "true";
                    validateRow(tbody);
                }
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    initAll();
});