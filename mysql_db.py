import MySQLdb as mysql


def sql_start():
    global base, cur
    base = mysql.connect(host="127.0.0.1", port=3306, user="shaturny", passwd="5555555555A", db="uni_tasks")
    cur = base.cursor()
    if base:
        print('DB connected OK!')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS subjects(id INT auto_increment, user_id INT, title VARCHAR(255), primary key (id))')
    cur.execute(
        'CREATE TABLE IF NOT EXISTS tasks(id INT auto_increment, user_id INT, '
        'subject_id INT, title VARCHAR(255), description VARCHAR(255), deadline DATETIME, '
        'important_degree INT, status BOOL, primary key (id), FOREIGN KEY (subject_id) REFERENCES subjects(id))')
    base.commit()


async def sql_add_task(state):
    async with state.proxy() as data:
        cur.execute(
            'INSERT INTO uni_tasks.tasks (user_id, subject_id, title, description, deadline, important_degree, status) '
            'VALUES (%s, %s, %s, %s, %s, %s, 0)', tuple(data.values()))
        base.commit()


async def sql_complete_task(id, user_id):
    cur.execute(
        'UPDATE uni_tasks.tasks SET status=mod(status+1, 2) WHERE id=%s and user_id=%s', (id, user_id))
    base.commit()


async def sql_remove_task(id, user_id):
    cur.execute(
        'DELETE FROM uni_tasks.tasks WHERE id=%s and user_id=%s', (id, user_id))
    base.commit()


async def sql_remove_subject(id, user_id):
    cur.execute(
        'DELETE FROM uni_tasks.subjects WHERE id=%s and user_id=%s', (id, user_id))
    base.commit()


async def sql_read_one_task(task_id, user_id):
    cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, deadline, important_degree, status "
                "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                "WHERE t.id = %s AND t.user_id = %s ORDER BY t.title", (task_id, user_id))
    res = cur.fetchall()[0]
    return res


async def sql_read_tasks(user_id, mode='all'):
    if mode == 'all':
        cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, deadline, important_degree, status "
                    "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                    "WHERE t.user_id = %s ORDER BY t.title", (user_id,))
    elif mode == 'day':
        cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, time(deadline), important_degree, status, "
                    "TIMEDIFF(deadline, sysdate())"
                    "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                    "WHERE date(sysdate()) <= deadline AND deadline <= date(DATE_ADD(sysdate(), INTERVAL 1 DAY)) "
                    "AND t.user_id = %s AND status=0 ORDER BY t.title", (user_id,))
    elif mode == 'week':
        cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, deadline, important_degree, status "
                    "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                    "WHERE date(sysdate()) <= deadline AND deadline <= date(DATE_ADD(sysdate(), INTERVAL 7 DAY)) "
                    "AND t.user_id = %s AND status=0 ORDER BY t.title", (user_id,))
    res = cur.fetchall()
    return res


async def sql_read_day_schedul(user_id, title, description):
    cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, deadline, important_degree, status, "
                "TIMEDIFF(deadline, DATE_ADD(sysdate(), INTERVAL 1 SECOND))"
                "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                "WHERE t.user_id = %s AND t.title = %s AND description = %s",
                (user_id, title, description))
    res = cur.fetchall()[0]
    return res


async def sql_read_custom_schedul(user_id, task_id):
    cur.execute("SELECT t.id, t.user_id, sb.title, t.title, description, deadline "
                "FROM uni_tasks.tasks t INNER JOIN uni_tasks.subjects sb on t.subject_id = sb.id "
                "WHERE t.user_id = %s AND t.id = %s",
                (user_id, task_id))
    res = cur.fetchall()
    return res


async def sql_add_subject(state):
    async with state.proxy() as data:
        cur.execute(
            'INSERT INTO uni_tasks.subjects (user_id, title) '
            'VALUES (%s, %s)', tuple(data.values()))
        base.commit()


async def sql_read_subjects(user_id):
    cur.execute("SELECT * FROM uni_tasks.subjects WHERE user_id = %s ORDER BY title", (user_id,))
    res = cur.fetchall()
    return res
