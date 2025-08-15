import json

def ask_question(question_data):
    """
    รับ dict ของคำถามรูปแบบ
    {
      "question": str,
      "options": [
        {
          "option": str,
          "result": [...],               # อาจมี
          "next_question": {...},       # อาจมี (object)
          "next_questions": [...],      # อาจมี (list)
          "sub_questions": [...],       # อาจมี (list)
          "note": str,                  # อาจมี (ข้อความเฉย ๆ)
          "follow_ups": [...],          # อาจมี (list ของคำถาม object เพิ่มเติม)
        },
        ...
      ]
    }
    """
    while True:
        print("\nคำถาม: " + question_data.get("question", "[ไม่พบคำถาม]"))
        options = question_data.get("options", [])
        if not options:
            print("[ไม่พบตัวเลือกคำตอบ]")
            return True

        for idx, opt in enumerate(options, 1):
            print(f"{idx}. {opt['option']}")
        ans = input("ตอบ (พิมพ์เลข): ").strip()
        if not ans.isdigit() or not (1 <= int(ans) <= len(options)):
            print("กรุณาเลือกหมายเลขคำตอบให้ถูกต้อง")
            continue

        selected = options[int(ans) - 1]

        if "note" in selected:
            print(selected["note"])


        if "result" in selected:
            print("\n>>> ผลลัพธ์สำหรับคุณ:")
            for r in selected["result"]:
                print("-", r)
            return True 

        elif "next_question" in selected:
 
            return ask_question(selected["next_question"])

        elif "next_questions" in selected:

            for q in selected["next_questions"]:
                done = ask_question(q)
                if done:
                    return True
            return True

        elif "sub_questions" in selected:
            for q in selected["sub_questions"]:
                done = ask_question(q)
                if done:
                    return True
            return True

        elif "follow_ups" in selected:
            for q in selected["follow_ups"]:
                done = ask_question(q)
                if done:
                    return True
            return True

        else:
            print("[ไม่มีข้อมูลถัดไป]")
            return True

def main():
    with open("cases.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n🎓 ยินดีต้อนรับสู่ระบบแนะนำสายการเรียน")

    case_names = [c["case"] for c in data.get("cases", [])]
    for i, name in enumerate(case_names, 1):
        print(f"{i}. {name}")

    while True:
        c_choice = input("เลือก (พิมพ์เลข): ").strip()
        if c_choice.isdigit() and 1 <= int(c_choice) <= len(case_names):
            case_name = case_names[int(c_choice) - 1]
            break
        else:
            print("กรุณาเลือกหมายเลขที่ถูกต้อง")

    case = next(c for c in data["cases"] if c["case"] == case_name)


    branches = case.get("branches", [])
    if len(branches) > 1:
        print("\nโปรดเลือกหัวข้อย่อยที่สนใจ:")
        for i, b in enumerate(branches, 1):
            title = b.get("branch") or b.get("question") or f"Branch {i}"
            print(f"{i}. {title}")
        while True:
            b_choice = input("เลือก (พิมพ์เลข): ").strip()
            if b_choice.isdigit() and 1 <= int(b_choice) <= len(branches):
                branch = branches[int(b_choice) - 1]
                break
            else:
                print("กรุณาเลือกหมายเลขที่ถูกต้อง")
    elif len(branches) == 1:
        branch = branches[0]
    else:
        print("ไม่มีหัวข้อย่อยในเคสนี้")
        return

    follow_ups = []
    if "next_questions" in branch:
        follow_ups.extend(branch["next_questions"])
    else:
        follow_ups.append(branch)

    for q in follow_ups:
        finished = ask_question(q)
        if finished:
            break

if __name__ == "__main__":
    main()
