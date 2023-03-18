class Config():
    DefaultBorder = 'QLineEdit{ border: 2px solid #373C66; color: white; border-radius: 15px; padding: 5px 10px;outline: none; }'
    RedBorder = 'QLineEdit{ border: 2px solid red; color: white; border-radius: 15px; padding: 5px 10px;outline: none; } QLineEdit:focus{ border-color: #947E45; }'
    CriticalBug = 'background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(251, 61, 61, 255), stop:1 rgba(152, 38, 38, 255));border-radius: 25px;'
    MediumBug = 'background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 149, 26, 255), stop:1 rgba(255, 187, 13, 255));border-radius: 25px;'
    NonCriticalBug = 'background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(16, 148, 53, 255), stop:1 rgba(29, 215, 81, 255));border-radius: 25px;'
