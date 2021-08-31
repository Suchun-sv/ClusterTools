from PostMessage import Mail, Wechat


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostMessage")
    parser.add_argument('-s', '--subject')
    parser.add_argument('-c', '--content', default='这是一条空消息')
    parser.add_argument('-t', '--type', default='mail')
    args = parser.parse_args()
    assert args.type in ['wechat', 'mail']
    if args.type == "wechat":
        Wechat.P(args.subject, args.content)
    elif args.type == "mail":
        Mail.P(args.subject, args.content)