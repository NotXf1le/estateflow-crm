from crm.bootstrap import create_application


def main() -> None:
    app = create_application()
    app.mainloop()


if __name__ == "__main__":
    main()
